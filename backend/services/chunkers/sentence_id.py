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
IndonesianSentenceSplitter — sentence chunker for Bahasa Indonesia and 23+ languages.

Default mode (language='id'): pure stdlib regex with Indonesian abbreviation list.
When pysbd is installed and language is one of its 23 supported codes, pysbd is
used automatically; for any other language the regex splitter is used as fallback.

Limitations:
- Quoted speech spanning multiple paragraphs is not handled.
- Bullet list items ending with '.' may produce false splits — prefer
  MarkdownStructureChunker for bullet-heavy content.
"""

import re
from collections.abc import Callable

try:
    import pysbd as _pysbd

    _PYSBD_LANGUAGES: frozenset[str] = frozenset(
        {
            "am",
            "ar",
            "bg",
            "da",
            "de",
            "el",
            "en",
            "es",
            "fa",
            "fr",
            "hi",
            "hy",
            "it",
            "ja",
            "kk",
            "mr",
            "my",
            "nl",
            "pl",
            "ru",
            "sk",
            "ur",
            "zh",
        }
    )
except ImportError:
    _pysbd = None  # type: ignore[assignment]
    _PYSBD_LANGUAGES = frozenset()

from .base import BaseChunker

# ---------------------------------------------------------------------------
# Abbreviation list — extend by adding entries to this frozenset.
# Entries WITH period (e.g. "Dr.") are checked against the word+punct token.
# Entries WITHOUT period (e.g. "UU", "Pasal") guard against "UU. Pasal..." splits.
# ---------------------------------------------------------------------------
ABBREV_ID: frozenset[str] = frozenset(
    {
        # Gelar / sapaan
        "Dr.",
        "Drs.",
        "Dra.",
        "Prof.",
        "Ir.",
        "Hj.",
        "H.",
        "Tn.",
        "Ny.",
        "Sdr.",
        "Sdri.",
        "S.H.",
        "S.E.",
        "M.M.",
        "M.Si.",
        "M.T.",
        "Ph.D.",
        "S.Kom.",
        "S.T.",
        # Singkatan umum
        "dll.",
        "dsb.",
        "dst.",
        "yth.",
        "a.n.",
        "u.p.",
        "u.b.",
        "d.a.",
        "s.d.",
        "tgl.",
        "hal.",
        "No.",
        "No",
        "Vol.",
        "Hlm.",
        "cet.",
        "ed.",
        # Lokasi
        "Jl.",
        "Jln.",
        "Kel.",
        "Kec.",
        "Kab.",
        "Prov.",
        "RT.",
        "RW.",
        "Gg.",
        # Hukum (without period — these appear before space, not before ".")
        "UU",
        "PP",
        "Perpres",
        "Permen",
        "Permendag",
        "Permenkes",
        "Perda",
        "Kepres",
        "Inpres",
        "Pasal",
        "Ayat",
        "KUHP",
        "KUHAP",
        "KUHPerdata",
        # Bulan singkat
        "Jan.",
        "Feb.",
        "Mar.",
        "Apr.",
        "Jun.",
        "Jul.",
        "Agt.",
        "Sep.",
        "Okt.",
        "Nov.",
        "Des.",
        # Lain-lain
        "vs.",
        "cf.",
        "ca.",
        "e.g.",
        "i.e.",
        "etc.",
        "a.l.",
    }
)

# Matches [.!?]+ followed by whitespace followed by an uppercase letter, quote,
# or open-parenthesis — the canonical lookahead for sentence start in Indonesian.
# Digits are intentionally excluded from lookahead so "No. 11 Tahun..." never splits.
_BOUNDARY_RE = re.compile(r'([.!?]+)\s+(?=[A-Z"\'\(])')


def _split_sentences(text: str) -> list[str]:
    """
    Split *text* into sentences using abbreviation-aware boundary detection.

    Algorithm:
    1. Find all positions matching _BOUNDARY_RE.
    2. For each match, extract the word token ending at the punctuation.
    3. Skip the split if that token is in ABBREV_ID.
    4. Split the text at remaining boundaries.
    """
    if not text.strip():
        return []

    boundaries: list[int] = []  # byte positions where a new sentence starts

    for m in _BOUNDARY_RE.finditer(text):
        # End of punctuation characters (start of trailing whitespace)
        punct_end = m.start() + len(m.group(1))

        # Walk backward to extract the word token that ends with the punctuation
        tok_start = m.start()
        while tok_start > 0 and not text[tok_start - 1].isspace():
            tok_start -= 1
        token = text[tok_start:punct_end]  # e.g. "Dr.", "No.", "ini."

        # Suppress split if token (or its de-punctuated form) is an abbreviation
        if token in ABBREV_ID or token.rstrip(".!?") in ABBREV_ID:
            continue

        # m.end() is the first character of the next sentence (lookahead not consumed)
        boundaries.append(m.end())

    if not boundaries:
        stripped = text.strip()
        return [stripped] if stripped else []

    sentences: list[str] = []
    prev = 0
    for pos in boundaries:
        sent = text[prev:pos].rstrip()
        if sent:
            sentences.append(sent)
        prev = pos

    tail = text[prev:].strip()
    if tail:
        sentences.append(tail)

    return sentences


# ---------------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------------


class IndonesianSentenceSplitter(BaseChunker):
    """
    Groups sentences into chunks with configurable sentence count and overlap.

    Params:
        language (str): language code (default 'id'). If pysbd is installed and
            the code is one of its 23 supported languages, pysbd is used;
            otherwise falls back to the regex splitter (works well for 'id').
        max_sentences_per_chunk (int): max sentences per chunk  (default 5)
        overlap_sentences (int): sentences repeated at the start of next chunk  (default 1)
        min_chunk_chars (int): chunks below this length are merged with the next  (default 100)

    Limitations documented in module docstring.
    """

    def chunk(self, text: str, **params) -> list[dict]:
        language: str = params.get("language", "id")
        max_sents: int = params.get("max_sentences_per_chunk", 5)
        overlap: int = params.get("overlap_sentences", 1)
        min_chars: int = params.get("min_chunk_chars", 100)

        if overlap >= max_sents:
            raise ValueError(
                f"overlap_sentences ({overlap}) must be less than "
                f"max_sentences_per_chunk ({max_sents})"
            )

        if not text:
            return []

        splitter: Callable[[str], list[str]]
        if _pysbd is not None and language in _PYSBD_LANGUAGES:
            _seg = _pysbd.Segmenter(language=language, clean=False)

            def splitter(t: str) -> list[str]:
                return [s for s in _seg.segment(t) if s.strip()]

        else:
            splitter = _split_sentences

        sentences = splitter(text)
        if not sentences:
            return []

        # Group sentences into raw chunks
        step = max_sents - overlap
        raw: list[dict] = []
        start = 0

        while start < len(sentences):
            end = min(start + max_sents, len(sentences))
            group = sentences[start:end]
            chunk_text = " ".join(group)

            # overlap_start_chars: chars shared with previous chunk
            if start == 0:
                overlap_start_chars = 0
            else:
                ov_count = min(overlap, len(group))
                overlap_start_chars = len(" ".join(group[:ov_count]))

            # overlap_end_chars: chars shared with next chunk
            next_start = start + step
            if next_start >= len(sentences):
                overlap_end_chars = 0
            else:
                ov_end = group[max(0, len(group) - overlap) :]
                overlap_end_chars = len(" ".join(ov_end))

            raw.append(
                {
                    "text": chunk_text,
                    "overlap_start_chars": overlap_start_chars,
                    "overlap_end_chars": overlap_end_chars,
                }
            )
            start = next_start

        # Merge chunks below min_chars into their successor
        merged = _merge_short(raw, min_chars)

        return [
            {
                "index": i,
                "text": c["text"],
                "char_count": len(c["text"]),
                "overlap_start_chars": c["overlap_start_chars"],
                "overlap_end_chars": c["overlap_end_chars"],
            }
            for i, c in enumerate(merged)
        ]


def _merge_short(chunks: list[dict], min_chars: int) -> list[dict]:
    """Merge chunks shorter than min_chars into the next chunk."""
    if not chunks:
        return []
    result: list[dict] = []
    pending_text = ""
    pending_ov_start = 0

    for i, c in enumerate(chunks):
        combined = (
            (pending_text + " " + c["text"]).strip() if pending_text else c["text"]
        )
        ov_start = pending_ov_start if pending_text else c["overlap_start_chars"]

        if len(combined) < min_chars and i < len(chunks) - 1:
            # Too short and not the last chunk — defer to next iteration
            pending_text = combined
            pending_ov_start = ov_start
        else:
            result.append(
                {
                    "text": combined,
                    "overlap_start_chars": ov_start,
                    "overlap_end_chars": c["overlap_end_chars"],
                }
            )
            pending_text = ""
            pending_ov_start = 0

    return result
