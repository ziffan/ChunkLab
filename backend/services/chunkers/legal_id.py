# Copyright [2026] Ziffan (Ziffany Firdinal)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
LegalStructureChunker — splits Indonesian regulatory text (UU/PP/Perpres/Perda)
at legal unit boundaries (Pasal, BAB, Ayat).

Structural reference: UU No. 12/2011 jo. UU No. 13/2022, Lampiran II.

Limitations:
- Quoted speech spanning multiple paragraphs is not detected.
- BAB section title on a separate line from "BAB I" is not captured in breadcrumb.
- unit="ayat" is not yet implemented; falls back to unit="pasal".
"""

import re
from dataclasses import dataclass, field as dc_field

from .base import BaseChunker
from .recursive import RecursiveCharacterChunker

_M = re.MULTILINE  # anchors ^ to start of each line

# ── Top-level section markers ─────────────────────────────────────────────────
_RE_RAHMAT = re.compile(r"^DENGAN\s+RAHMAT\s+TUHAN\s+YANG\s+MAHA\s+ESA", _M)
_RE_MENIMBANG = re.compile(r"^Menimbang\s*:", _M)
_RE_MENGINGAT = re.compile(r"^Mengingat\s*:", _M)
_RE_MEMUTUSKAN = re.compile(r"^MEMUTUSKAN\s*:", _M)
_RE_MENETAPKAN = re.compile(r"^Menetapkan\s*:", _M)
_RE_PENJELASAN = re.compile(r"^PENJELASAN(?:\s+ATAS)?", _M)
_RE_LAMPIRAN = re.compile(r"^LAMPIRAN(?:\s+[IVX]+)?", _M)

# ── Hierarchy markers (BATANG TUBUH) — from Section 3 of reference ─────────────
_RE_BAB = re.compile(r"^BAB\s+([IVXLCDM]+[A-Z]?)\b", _M)
_RE_BAGIAN = re.compile(
    r"^Bagian\s+(Kesatu|Kedua|Ketiga|Keempat|Kelima|Keenam|Ketujuh|Kedelapan"
    r"|Kesembilan|Kesepuluh|Kesebelas|Keduabelas|Ketigabelas|Keempatbelas"
    r"|Kelimabelas|Keenambelas|Ketujuhbelas|Kedelapanbelas|Kesembilanbelas"
    r"|Keduapuluh)\b",
    _M,
)
_RE_PARAGRAF = re.compile(r"^Paragraf\s+(\d+)\b", _M)
_RE_PASAL = re.compile(r"^Pasal\s+(\d+[A-Z]?)\s*$", _M)  # Arabic, anchored EOL
_RE_PASAL_ROMAN = re.compile(r"^Pasal\s+([IVXLCDM]+)\s*$", _M)  # Amendment UU
_RE_AMENDMENT = re.compile(
    r"PERUBAHAN\s+(?:KEDUA|KETIGA|KE-?\d+)?\s*ATAS\s+UNDANG-UNDANG", re.IGNORECASE
)

# ── PENJELASAN sub-structure ─────────────────────────────────────────────────
_RE_PEN_PDP = re.compile(r"^II\.\s+PASAL\s+DEMI\s+PASAL", _M)
_RE_PEN_PASAL = re.compile(r"^\s*Pasal\s+(\d+[A-Z]?)\s*$", _M)  # allows leading spaces


# ── Parent stack entry ────────────────────────────────────────────────────────


@dataclass
class _Entry:
    level: int  # 1 = BAB, 2 = Bagian, 3 = Paragraf
    marker: str  # "BAB", "Bagian", "Paragraf"
    number: str  # "I", "Kedua", "1"
    title: str = dc_field(default="")


def _update_stack(
    stack: list[_Entry], level: int, marker: str, number: str, title: str = ""
) -> None:
    """Pop entries at or deeper than level, then push new entry."""
    while stack and stack[-1].level >= level:
        stack.pop()
    stack.append(_Entry(level, marker, number, title))


def _build_path(stack: list[_Entry], pasal_number: str = "") -> str:
    """Build 'BAB I > Bagian Kedua > Pasal 5' breadcrumb from stack."""
    parts = []
    for e in stack:
        label = f"{e.marker} {e.number}"
        if e.title:
            label += f" {e.title}"
        parts.append(label)
    if pasal_number:
        parts.append(f"Pasal {pasal_number}")
    return " > ".join(parts)


# ── Main chunker ──────────────────────────────────────────────────────────────


class LegalStructureChunker(BaseChunker):
    """
    Chunks Indonesian regulatory documents at legal unit boundaries.

    Params:
        unit (str): "pasal" | "bab" | "auto"  (default "pasal"; "ayat" falls back to "pasal")
        include_parent_context (bool): prepend [BAB > Pasal] breadcrumb  (default True)
        attach_path_metadata (bool): embed _legal_path in returned dict  (default True)
        max_chunk_chars (int): hard cap; overflow → RecursiveCharacterChunker  (default 4000)
    """

    def chunk(self, text: str, **params) -> list[dict]:
        unit: str = params.get("unit", "pasal")
        include_parent_context: bool = params.get("include_parent_context", True)
        max_chunk_chars: int = params.get("max_chunk_chars", 4000)

        if not text.strip():
            return []

        is_amendment = bool(_RE_AMENDMENT.search(text))

        if unit == "auto":
            unit = self._auto_unit(text, is_amendment)
        if unit == "ayat":
            unit = "pasal"  # ayat not yet implemented

        raw = self._segment(text, unit, include_parent_context, is_amendment)

        # Apply max_chunk_chars: oversized chunks → recursive fallback
        _rc = RecursiveCharacterChunker()
        result: list[dict] = []
        for chunk in raw:
            if len(chunk["text"]) > max_chunk_chars:
                subs = _rc.chunk(
                    chunk["text"], chunk_size=max_chunk_chars, chunk_overlap=0
                )
                for sub in subs:
                    result.append(
                        {
                            **sub,
                            "_legal_section": chunk["_legal_section"],
                            "_legal_path": chunk["_legal_path"],
                            "_legal_unit": unit,
                            "_legal_number": chunk["_legal_number"],
                        }
                    )
            else:
                result.append(chunk)

        for i, c in enumerate(result):
            c["index"] = i
        return result

    # ── unit auto-selection ───────────────────────────────────────────────────

    def _auto_unit(self, text: str, is_amendment: bool) -> str:
        re_p = _RE_PASAL_ROMAN if is_amendment else _RE_PASAL
        pasals = list(re_p.finditer(text))
        n = len(pasals)
        if n < 5:
            return "bab"
        if n >= 50:
            positions = [m.start() for m in pasals] + [len(text)]
            avg = sum(positions[i + 1] - positions[i] for i in range(n)) / n
            if avg > 2048:
                return "ayat"
        return "pasal"

    # ── main segmentation ─────────────────────────────────────────────────────

    def _segment(
        self,
        text: str,
        unit: str,
        include_parent_context: bool,
        is_amendment: bool,
    ) -> list[dict]:

        lines = text.splitlines(keepends=True)
        chunks: list[dict] = []
        stack: list[_Entry] = []
        accum: list[str] = []

        current_section = "JUDUL"
        current_pasal_no = ""
        in_pasal = False  # True after first Pasal seen (unit=pasal)
        in_pdp = False  # Inside PENJELASAN PASAL DEMI PASAL
        re_pasal = _RE_PASAL_ROMAN if is_amendment else _RE_PASAL

        # ── closure: emit accumulated buffer as one chunk ────────────────────

        def flush(section: str = "", number: str = "", path_override: str = "") -> None:
            nonlocal accum, current_pasal_no, in_pasal
            raw = "".join(accum).strip()
            if not raw:
                accum = []
                return
            sec = section or current_section
            num = number or current_pasal_no
            if path_override:
                path = path_override
            elif sec in ("BATANG_TUBUH", "PENJELASAN"):
                path = _build_path(stack, num if sec == "BATANG_TUBUH" else "")
            else:
                path = ""

            display = f"[{path}]\n\n{raw}" if (include_parent_context and path) else raw
            chunks.append(
                {
                    "index": len(chunks),
                    "text": display,
                    "char_count": len(display),
                    "overlap_start_chars": 0,
                    "overlap_end_chars": 0,
                    "_legal_section": sec,
                    "_legal_path": path,
                    "_legal_unit": unit,
                    "_legal_number": num,
                }
            )
            accum = []
            current_pasal_no = ""
            in_pasal = False

        # ── line-by-line scanner ─────────────────────────────────────────────

        for line in lines:
            s = line.strip()

            # ── Global section transitions (highest priority) ─────────────────

            if _RE_PENJELASAN.match(s) and current_section != "PENJELASAN":
                flush()
                current_section = "PENJELASAN"
                in_pdp = False
                accum = [line]
                continue

            if _RE_LAMPIRAN.match(s):
                flush()
                current_section = "LAMPIRAN"
                accum = [line]
                continue

            # ── JUDUL ─────────────────────────────────────────────────────────

            if current_section == "JUDUL":
                if _RE_RAHMAT.match(s) or _RE_MENIMBANG.match(s):
                    flush(section="JUDUL")
                    current_section = "PEMBUKAAN"
                    accum = [line]
                    continue
                if _RE_BAB.match(s) or re_pasal.match(s):
                    flush(section="JUDUL")
                    current_section = "BATANG_TUBUH"
                    # fall through to BATANG_TUBUH block
                else:
                    accum.append(line)
                    continue

            # ── PEMBUKAAN ─────────────────────────────────────────────────────

            if current_section == "PEMBUKAAN":
                boundary = None
                for re_k in (
                    _RE_MENIMBANG,
                    _RE_MENGINGAT,
                    _RE_MEMUTUSKAN,
                    _RE_MENETAPKAN,
                ):
                    if re_k.match(s):
                        boundary = re_k
                        break

                if boundary:
                    # Each konsiderans block is its own chunk
                    if boundary is not _RE_MENIMBANG or not _RE_MENIMBANG.match(
                        "".join(accum).strip()
                    ):
                        flush(section="PEMBUKAAN")
                    accum = [line]
                    continue

                if _RE_BAB.match(s) or re_pasal.match(s):
                    flush(section="PEMBUKAAN")
                    current_section = "BATANG_TUBUH"
                    # fall through to BATANG_TUBUH block
                else:
                    accum.append(line)
                    continue

            # ── PENJELASAN ────────────────────────────────────────────────────

            if current_section == "PENJELASAN":
                if _RE_PEN_PDP.match(s):
                    flush(section="PENJELASAN")
                    in_pdp = True
                    accum = [line]
                    continue
                if in_pdp:
                    m = _RE_PEN_PASAL.match(s)
                    if m:
                        old_num = current_pasal_no
                        flush(
                            section="PENJELASAN",
                            path_override=(
                                f"Pasal {old_num} (Penjelasan)" if old_num else ""
                            ),
                        )
                        current_pasal_no = m.group(1)
                        accum = [line]
                        continue
                accum.append(line)
                continue

            # ── LAMPIRAN ──────────────────────────────────────────────────────

            if current_section == "LAMPIRAN":
                if _RE_LAMPIRAN.match(s) and accum:
                    flush(section="LAMPIRAN")
                accum.append(line)
                continue

            # ── BATANG TUBUH ──────────────────────────────────────────────────

            if current_section == "BATANG_TUBUH":
                m_bab = _RE_BAB.match(s)
                m_bagian = _RE_BAGIAN.match(s)
                m_paragraf = _RE_PARAGRAF.match(s)
                m_pasal = re_pasal.match(s)

                if m_bab:
                    bab_num = m_bab.group(1)
                    bab_rest = s[m_bab.end() :].strip()
                    if unit == "bab":
                        if accum:
                            flush()
                        _update_stack(stack, 1, "BAB", bab_num, bab_rest)
                        current_pasal_no = bab_num
                        in_pasal = True
                        accum.append(line)
                    else:
                        # unit=pasal: BAB boundary flushes current Pasal (if any)
                        if in_pasal:
                            flush()
                        _update_stack(stack, 1, "BAB", bab_num, bab_rest)
                        # Do NOT accumulate the BAB header line itself
                    continue

                if m_bagian:
                    bag_num = m_bagian.group(1)
                    bag_rest = s[m_bagian.end() :].strip()
                    _update_stack(stack, 2, "Bagian", bag_num, bag_rest)
                    if unit == "bab":
                        accum.append(line)
                    continue

                if m_paragraf:
                    par_num = m_paragraf.group(1)
                    par_rest = s[m_paragraf.end() :].strip()
                    _update_stack(stack, 3, "Paragraf", par_num, par_rest)
                    if unit == "bab":
                        accum.append(line)
                    continue

                if m_pasal:
                    pasal_num = m_pasal.group(1)
                    if unit in ("pasal", "auto"):
                        if in_pasal:
                            flush()
                        current_pasal_no = pasal_num
                        in_pasal = True
                        accum = [line]
                    else:
                        accum.append(line)
                    continue

                # Regular content line
                if in_pasal or unit == "bab":
                    accum.append(line)
                # else: discard (content before first Pasal in BATANG_TUBUH)
                continue

        # Final flush
        flush()
        return chunks
