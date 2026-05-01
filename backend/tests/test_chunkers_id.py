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
Tests for Indonesian-specific chunkers:
  - IndonesianSentenceSplitter (strategy "sentence_id")
  - LegalStructureChunker (strategy "legal_id")

Validation checklist from LEGAL_STRUCTURE_REFERENCE_ID.md Section 8.
"""

import json
import os

import pytest

from backend.services.chunkers.legal_id import LegalStructureChunker
from backend.services.chunkers.sentence_id import (
    IndonesianSentenceSplitter,
    _split_sentences,
)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# IndonesianSentenceSplitter
# ---------------------------------------------------------------------------


class TestIndonesianSentenceSplitter:
    def setup_method(self):
        self.chunker = IndonesianSentenceSplitter()

    def test_empty_text_returns_empty(self):
        assert self.chunker.chunk("") == []

    def test_whitespace_only_returns_empty(self):
        assert self.chunker.chunk("   \n\n  ") == []

    # --- Spec test cases (from CHUNKLAB_V2_1_PATCH_PROMPT.md) ---

    def test_pasal_no_11_not_split(self):
        """'UU No. 11' must not produce a false split at 'No.'"""
        fixture = load_fixture("sentence_id.json")
        cfg = fixture["edge_no_11_split"]
        sents = _split_sentences(cfg["text"])
        assert (
            len(sents) == cfg["expected_count"]
        ), f"Expected {cfg['expected_count']} sentences, got {len(sents)}: {sents}"

    def test_abbreviation_dr_not_split(self):
        """'Dr.' must not trigger a sentence boundary."""
        fixture = load_fixture("sentence_id.json")
        cfg = fixture["edge_abbreviation_dr"]
        sents = _split_sentences(cfg["text"])
        assert (
            len(sents) == cfg["expected_count"]
        ), f"Expected {cfg['expected_count']} sentences, got {len(sents)}: {sents}"
        assert sents[0].startswith("Menurut Dr. Anwar")

    def test_min_chunk_chars_merging(self):
        """Short first chunk is merged into successor."""
        text = "Ok. Ini adalah kalimat yang sangat panjang untuk digunakan sebagai konten utama."
        result = self.chunker.chunk(
            text, max_sentences_per_chunk=5, overlap_sentences=0, min_chunk_chars=100
        )
        assert len(result) == 1
        assert "Ok." in result[0]["text"]

    # --- Abbreviation edge cases ---

    def test_multiple_titles_not_split(self):
        """Chained academic titles (Prof. Dr.) must not cause splits."""
        text = "Prof. Dr. Hj. Siti Rahma, S.H., M.H. menyatakan bahwa hal ini sudah diatur. Peraturan tersebut mengacu pada UU yang berlaku."
        sents = _split_sentences(text)
        assert len(sents) == 2
        assert sents[0].startswith("Prof.")

    def test_legal_abbrev_no_split(self):
        """UU and PP (without period) must not trigger splits."""
        text = "Ketentuan dalam UU No. 12 Tahun 2011 mengatur hal ini secara rinci. Peraturan lebih lanjut ditetapkan PP."
        sents = _split_sentences(text)
        assert len(sents) == 2

    def test_exclamation_splits_correctly(self):
        """Exclamation marks are valid sentence boundaries."""
        text = "Ayo segera mendaftar! Waktu pendaftaran segera berakhir."
        sents = _split_sentences(text)
        assert len(sents) == 2

    # --- Chunk structure ---

    def test_single_sentence_single_chunk(self):
        fixture = load_fixture("sentence_id.json")
        cfg = fixture["edge_single_sentence"]
        result = self.chunker.chunk(
            cfg["text"],
            max_sentences_per_chunk=cfg["max_sentences_per_chunk"],
            overlap_sentences=cfg["overlap_sentences"],
            min_chunk_chars=cfg["min_chunk_chars"],
        )
        assert len(result) == 1
        assert result[0]["overlap_start_chars"] == 0
        assert result[0]["overlap_end_chars"] == 0

    def test_first_chunk_no_overlap_start(self):
        fixture = load_fixture("sentence_id.json")
        cfg = fixture["happy_path"]
        result = self.chunker.chunk(
            cfg["text"],
            max_sentences_per_chunk=cfg["max_sentences_per_chunk"],
            overlap_sentences=cfg["overlap_sentences"],
            min_chunk_chars=cfg["min_chunk_chars"],
        )
        assert len(result) >= 1
        assert result[0]["overlap_start_chars"] == 0

    def test_overlap_nonzero_after_first(self):
        fixture = load_fixture("sentence_id.json")
        cfg = fixture["happy_path"]
        result = self.chunker.chunk(
            cfg["text"],
            max_sentences_per_chunk=cfg["max_sentences_per_chunk"],
            overlap_sentences=cfg["overlap_sentences"],
            min_chunk_chars=cfg["min_chunk_chars"],
        )
        assert len(result) >= 2
        for chunk in result[1:]:
            assert chunk["overlap_start_chars"] > 0

    def test_no_overlap_disjoint(self):
        fixture = load_fixture("sentence_id.json")
        cfg = fixture["edge_no_overlap"]
        result = self.chunker.chunk(
            cfg["text"],
            max_sentences_per_chunk=cfg["max_sentences_per_chunk"],
            overlap_sentences=cfg["overlap_sentences"],
            min_chunk_chars=cfg["min_chunk_chars"],
        )
        assert len(result) >= 2
        for chunk in result:
            assert chunk["overlap_start_chars"] == 0
            assert chunk["overlap_end_chars"] == 0

    def test_indices_sequential(self):
        fixture = load_fixture("sentence_id.json")
        cfg = fixture["happy_path"]
        result = self.chunker.chunk(
            cfg["text"],
            max_sentences_per_chunk=cfg["max_sentences_per_chunk"],
            overlap_sentences=cfg["overlap_sentences"],
            min_chunk_chars=cfg["min_chunk_chars"],
        )
        for i, chunk in enumerate(result):
            assert chunk["index"] == i

    def test_char_count_consistent(self):
        fixture = load_fixture("sentence_id.json")
        cfg = fixture["happy_path"]
        result = self.chunker.chunk(
            cfg["text"],
            max_sentences_per_chunk=cfg["max_sentences_per_chunk"],
            overlap_sentences=cfg["overlap_sentences"],
            min_chunk_chars=cfg["min_chunk_chars"],
        )
        for chunk in result:
            assert chunk["char_count"] == len(chunk["text"])

    def test_invalid_overlap_raises(self):
        with pytest.raises(ValueError, match="overlap_sentences"):
            self.chunker.chunk(
                "Kalimat satu. Kalimat dua.",
                max_sentences_per_chunk=3,
                overlap_sentences=3,
            )


# ---------------------------------------------------------------------------
# LegalStructureChunker — Section 8 checklist
# ---------------------------------------------------------------------------


class TestLegalStructureChunker:
    def setup_method(self):
        self.chunker = LegalStructureChunker()

    def _load(self, key):
        return load_fixture("legal_id.json")[key]

    # --- Baseline ---

    def test_empty_text_returns_empty(self):
        assert self.chunker.chunk("") == []

    def test_whitespace_only_returns_empty(self):
        assert self.chunker.chunk("   \n\n  ") == []

    # --- Checklist 1: Simple 5-Pasal UU, unit=pasal → 5 Pasal chunks ---

    def test_simple_5pasal_unit_pasal(self):
        cfg = self._load("simple_5pasal")
        result = self.chunker.chunk(
            cfg["text"],
            unit=cfg["unit"],
            include_parent_context=cfg["include_parent_context"],
        )
        pasal_chunks = [c for c in result if c["_legal_section"] == "BATANG_TUBUH"]
        assert len(pasal_chunks) == cfg["expected_pasal_count"], (
            f"Expected {cfg['expected_pasal_count']} Pasal chunks, "
            f"got {len(pasal_chunks)}: {[c['_legal_number'] for c in pasal_chunks]}"
        )

    def test_simple_5pasal_numbers(self):
        """Pasal numbers must be 1–5 in order."""
        cfg = self._load("simple_5pasal")
        result = self.chunker.chunk(
            cfg["text"], unit=cfg["unit"], include_parent_context=False
        )
        pasal_nums = [
            c["_legal_number"] for c in result if c["_legal_section"] == "BATANG_TUBUH"
        ]
        assert pasal_nums == ["1", "2", "3", "4", "5"]

    # --- Checklist 2: Multi-BAB with Bagian and Paragraf in breadcrumb ---

    def test_multibab_legal_path_includes_all_levels(self):
        cfg = self._load("multibab_with_bagian")
        result = self.chunker.chunk(
            cfg["text"],
            unit=cfg["unit"],
            include_parent_context=cfg["include_parent_context"],
        )
        pasal2 = next((c for c in result if c["_legal_number"] == "2"), None)
        assert pasal2 is not None, "Pasal 2 chunk not found"
        path = pasal2["_legal_path"]
        assert "BAB II" in path
        assert "Bagian Kesatu" in path
        assert "Paragraf 1" in path
        assert "Pasal 2" in path

    def test_multibab_pasal3_path_has_bagian_kedua(self):
        cfg = self._load("multibab_with_bagian")
        result = self.chunker.chunk(
            cfg["text"], unit=cfg["unit"], include_parent_context=False
        )
        pasal3 = next((c for c in result if c["_legal_number"] == "3"), None)
        assert pasal3 is not None
        assert "Bagian Kedua" in pasal3["_legal_path"]

    # --- Checklist 3: Inserted Pasal (28A, 28B) ---

    def test_inserted_pasal_28a_matched(self):
        cfg = self._load("inserted_pasal")
        result = self.chunker.chunk(
            cfg["text"],
            unit=cfg["unit"],
            include_parent_context=cfg["include_parent_context"],
        )
        pasal_nums = [
            c["_legal_number"] for c in result if c["_legal_section"] == "BATANG_TUBUH"
        ]
        assert "28A" in pasal_nums, f"Pasal 28A missing from chunks: {pasal_nums}"
        assert "28B" in pasal_nums, f"Pasal 28B missing from chunks: {pasal_nums}"

    def test_inserted_pasal_content_correct(self):
        cfg = self._load("inserted_pasal")
        result = self.chunker.chunk(
            cfg["text"], unit=cfg["unit"], include_parent_context=False
        )
        chunk_28a = next((c for c in result if c["_legal_number"] == "28A"), None)
        assert chunk_28a is not None
        assert "berhak untuk hidup" in chunk_28a["text"]

    # --- Checklist 4: "Dihapus." Pasal must not be skipped ---

    def test_dihapus_pasal_produces_chunk(self):
        cfg = self._load("dihapus_pasal")
        result = self.chunker.chunk(
            cfg["text"],
            unit=cfg["unit"],
            include_parent_context=cfg["include_parent_context"],
        )
        pasal4 = next((c for c in result if c["_legal_number"] == "4"), None)
        assert (
            pasal4 is not None
        ), "Pasal 4 (Dihapus) was skipped — must produce a chunk"
        assert "Dihapus" in pasal4["text"]

    # --- Checklist 5: Amendment UU — Roman Pasal I/II as boundaries ---

    def test_amendment_roman_pasal_boundaries(self):
        cfg = self._load("amendment_roman")
        result = self.chunker.chunk(
            cfg["text"],
            unit=cfg["unit"],
            include_parent_context=cfg["include_parent_context"],
        )
        pasal_nums = [
            c["_legal_number"] for c in result if c["_legal_section"] == "BATANG_TUBUH"
        ]
        assert "I" in pasal_nums, f"Pasal I missing: {pasal_nums}"
        assert "II" in pasal_nums, f"Pasal II missing: {pasal_nums}"
        assert len(pasal_nums) == cfg["expected_count"]

    def test_amendment_inner_arabic_pasal_not_boundary(self):
        """'Pasal 7' inside Pasal I body must NOT become its own chunk."""
        cfg = self._load("amendment_roman")
        result = self.chunker.chunk(
            cfg["text"], unit=cfg["unit"], include_parent_context=False
        )
        pasal_nums = [
            c["_legal_number"] for c in result if c["_legal_section"] == "BATANG_TUBUH"
        ]
        assert (
            "7" not in pasal_nums
        ), "Inner quoted 'Pasal 7' should not become a chunk boundary in amendment mode"

    # --- Checklist 6: PENJELASAN PASAL DEMI PASAL — one chunk per explanation ---

    def test_penjelasan_section_produced(self):
        cfg = self._load("penjelasan_pdp")
        result = self.chunker.chunk(
            cfg["text"],
            unit=cfg["unit"],
            include_parent_context=cfg["include_parent_context"],
        )
        penjelasan_chunks = [c for c in result if c["_legal_section"] == "PENJELASAN"]
        assert len(penjelasan_chunks) >= 1, "No PENJELASAN chunks produced"

    def test_penjelasan_pasal_demi_pasal_split(self):
        """After 'II. PASAL DEMI PASAL', each Pasal explanation is its own chunk."""
        cfg = self._load("penjelasan_pdp")
        result = self.chunker.chunk(
            cfg["text"], unit=cfg["unit"], include_parent_context=False
        )
        penjelasan_chunks = [c for c in result if c["_legal_section"] == "PENJELASAN"]
        # Should have: I. UMUM chunk + Pasal 1 explanation + Pasal 2 explanation
        assert (
            len(penjelasan_chunks) >= 3
        ), f"Expected at least 3 PENJELASAN chunks, got {len(penjelasan_chunks)}"

    # --- Checklist 7: LAMPIRAN — separate top-level treatment ---

    def test_lampiran_separate_section(self):
        cfg = self._load("lampiran")
        result = self.chunker.chunk(
            cfg["text"],
            unit=cfg["unit"],
            include_parent_context=cfg["include_parent_context"],
        )
        lampiran_chunks = [c for c in result if c["_legal_section"] == "LAMPIRAN"]
        assert len(lampiran_chunks) >= 1, "No LAMPIRAN chunks produced"

    def test_lampiran_not_merged_with_batang_tubuh(self):
        cfg = self._load("lampiran")
        result = self.chunker.chunk(
            cfg["text"], unit=cfg["unit"], include_parent_context=False
        )
        for c in result:
            if c["_legal_section"] == "LAMPIRAN":
                assert (
                    "Pasal 1" not in c["text"]
                ), "Batang tubuh content leaked into LAMPIRAN chunk"

    # --- Checklist 8: Tabulation stays inside parent Pasal chunk ---

    def test_tabulation_stays_in_pasal(self):
        cfg = self._load("tabulation_in_pasal")
        result = self.chunker.chunk(
            cfg["text"],
            unit=cfg["unit"],
            include_parent_context=cfg["include_parent_context"],
        )
        pasal5_chunks = [c for c in result if c["_legal_number"] == "5"]
        assert (
            len(pasal5_chunks) == 1
        ), f"Expected 1 chunk for Pasal 5 (with tabulation), got {len(pasal5_chunks)}"
        text = pasal5_chunks[0]["text"]
        assert (
            "a." in text and "b." in text and "c." in text
        ), "Tabulation items a/b/c must stay inside Pasal 5 chunk"

    # --- Inline Pasal format (PDF-converted documents) ---

    def test_inline_pasal_header_detected(self):
        """Pasal N followed by content on same line (PDF conversion artifact) is detected."""
        text = (
            "BAB I KETENTUAN UMUM\n"
            "Pasal 1 Dalam peraturan ini yang dimaksud dengan:\n"
            "1. Penyelenggara adalah badan hukum yang menyelenggarakan layanan.\n"
            "2. Pengguna adalah pihak yang menggunakan layanan.\n"
            "Pasal 2 Bentuk badan hukum terdiri atas:\n"
            "a. perseroan terbatas; dan\n"
            "b. koperasi.\n"
            "Pasal 3\n"
            "(1) Ketentuan ini berlaku sejak diundangkan.\n"
        )
        result = self.chunker.chunk(text, unit="pasal", include_parent_context=False)
        numbers = [c["_legal_number"] for c in result if c["_legal_section"] == "BATANG_TUBUH"]
        assert "1" in numbers, f"Pasal 1 (inline) not detected; got {numbers}"
        assert "2" in numbers, f"Pasal 2 (inline) not detected; got {numbers}"
        assert "3" in numbers, f"Pasal 3 (standalone) not detected; got {numbers}"

    def test_inline_pasal_no_false_positive_from_reference(self):
        """Cross-references like 'Pasal N ayat' or 'Pasal N huruf' are not treated as headers."""
        text = (
            "BAB I UMUM\n"
            "Pasal 1\n"
            "(1) Ketentuan sebagaimana dimaksud dalam\n"
            "Pasal 2 huruf a berlaku sejak ditetapkan.\n"
            "Pasal 2\n"
            "(1) Penyelenggara wajib mematuhi peraturan ini.\n"
        )
        result = self.chunker.chunk(text, unit="pasal", include_parent_context=False)
        numbers = [c["_legal_number"] for c in result if c["_legal_section"] == "BATANG_TUBUH"]
        # 'Pasal 2 huruf a' is a cross-reference — must NOT produce a third chunk
        assert numbers.count("2") == 1, (
            f"'Pasal 2 huruf a' falsely detected as header; chunks: {numbers}"
        )

    # --- is_amendment false positive guard ---

    def test_non_amendment_doc_with_amendment_reference_in_penjelasan(self):
        """POJK/PP that references an amendment UU inside PENJELASAN must not be
        misidentified as an amendment document — Arabic Pasal numbers must still work."""
        text = (
            "PERATURAN OTORITAS JASA KEUANGAN REPUBLIK INDONESIA\n"
            "NOMOR 40 TAHUN 2024\n"
            "TENTANG PERLINDUNGAN KONSUMEN\n"
            "\n"
            "DENGAN RAHMAT TUHAN YANG MAHA ESA\n"
            "\n"
            "Menimbang :\n"
            "a. bahwa untuk melindungi konsumen perlu menetapkan peraturan;\n"
            "\n"
            "MEMUTUSKAN:\n"
            "Menetapkan:\n"
            "\n"
            "BAB I\n"
            "KETENTUAN UMUM\n"
            "\n"
            "Pasal 1\n"
            "Dalam Peraturan Otoritas Jasa Keuangan ini yang dimaksud dengan:\n"
            "1. Konsumen adalah pihak yang memanfaatkan layanan jasa keuangan.\n"
            "\n"
            "Pasal 2\n"
            "(1) Penyelenggara wajib melindungi data pribadi Konsumen.\n"
            "\n"
            "PENJELASAN\n"
            "Pasal 1\n"
            "Ketentuan ini sesuai dengan Perubahan Kedua atas Undang-Undang\n"
            "Nomor 11 Tahun 2008 tentang Informasi dan Transaksi Elektronik.\n"
        )
        result = self.chunker.chunk(text, unit="pasal", include_parent_context=False)
        bt_numbers = [c["_legal_number"] for c in result if c["_legal_section"] == "BATANG_TUBUH"]
        assert "1" in bt_numbers, f"Pasal 1 not detected; BATANG_TUBUH numbers: {bt_numbers}"
        assert "2" in bt_numbers, f"Pasal 2 not detected; BATANG_TUBUH numbers: {bt_numbers}"
        assert len(bt_numbers) >= 2, f"Expected >=2 BATANG_TUBUH chunks, got {bt_numbers}"

    # --- Checklist 9: max_chunk_chars fallback inherits legal_path ---

    def test_max_chunk_chars_fallback_inherits_metadata(self):
        cfg = self._load("max_chunk_chars_fallback")
        result = self.chunker.chunk(
            cfg["text"],
            unit=cfg["unit"],
            include_parent_context=cfg["include_parent_context"],
            max_chunk_chars=cfg["max_chunk_chars"],
        )
        pasal10_chunks = [c for c in result if c["_legal_number"] == "10"]
        # Pasal 10 text > max_chunk_chars → split into multiple sub-chunks
        assert (
            len(pasal10_chunks) >= 2
        ), f"Expected Pasal 10 to be split by fallback, got {len(pasal10_chunks)} chunk(s)"
        # All sub-chunks must share the same legal_path
        paths = {c["_legal_path"] for c in pasal10_chunks}
        assert len(paths) == 1, f"Sub-chunks have different legal_path values: {paths}"

    # --- Metadata schema ---

    def test_legal_metadata_fields_present(self):
        """Every chunk must carry all four _legal_* fields."""
        cfg = self._load("simple_5pasal")
        result = self.chunker.chunk(
            cfg["text"], unit="pasal", include_parent_context=False
        )
        for chunk in result:
            assert "_legal_section" in chunk
            assert "_legal_path" in chunk
            assert "_legal_unit" in chunk
            assert "_legal_number" in chunk

    def test_indices_sequential(self):
        cfg = self._load("simple_5pasal")
        result = self.chunker.chunk(
            cfg["text"], unit="pasal", include_parent_context=False
        )
        for i, chunk in enumerate(result):
            assert chunk["index"] == i

    def test_char_count_consistent(self):
        cfg = self._load("simple_5pasal")
        result = self.chunker.chunk(
            cfg["text"], unit="pasal", include_parent_context=False
        )
        for chunk in result:
            assert chunk["char_count"] == len(chunk["text"])
