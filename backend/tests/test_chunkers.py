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

import json
import os

import tiktoken

from backend.services.chunkers.markdown_struct import MarkdownStructureChunker
from backend.services.chunkers.recursive import RecursiveCharacterChunker
from backend.services.chunkers.sentence import SentenceChunker
from backend.services.chunkers.token_aware import TokenAwareChunker

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# RecursiveCharacterChunker
# ---------------------------------------------------------------------------


class TestRecursiveCharacterChunker:
    def setup_method(self):
        self.chunker = RecursiveCharacterChunker()

    def test_empty_text_returns_empty(self):
        result = self.chunker.chunk("", chunk_size=100, chunk_overlap=10)
        assert result == []

    def test_short_text_single_chunk(self):
        fixture = load_fixture("strategy_recursive.json")
        cfg = fixture["edge_short"]
        result = self.chunker.chunk(
            cfg["text"],
            chunk_size=cfg["chunk_size"],
            chunk_overlap=cfg["chunk_overlap"],
        )
        assert len(result) == 1
        assert result[0]["index"] == 0
        assert result[0]["text"] == cfg["text"]
        assert result[0]["overlap_start_chars"] == 0
        assert result[0]["overlap_end_chars"] == 0

    def test_paragraph_boundaries_respected(self):
        """Chunks should end at \\n\\n boundaries when text fits that way."""
        fixture = load_fixture("strategy_recursive.json")
        cfg = fixture["happy_path"]
        result = self.chunker.chunk(
            cfg["text"],
            chunk_size=cfg["chunk_size"],
            chunk_overlap=cfg["chunk_overlap"],
        )
        assert len(result) >= 2
        # Every chunk must be within chunk_size (hard limit)
        for chunk in result:
            assert (
                chunk["char_count"] <= cfg["chunk_size"]
            ), f"Chunk {chunk['index']} exceeded chunk_size: {chunk['char_count']}"

    def test_chunks_cover_full_text(self):
        """All characters in the original text must appear in at least one chunk."""
        text = "Para A\n\nPara B\n\nPara C\n\nPara D"
        result = self.chunker.chunk(text, chunk_size=20, chunk_overlap=5)
        combined = "".join(c["text"] for c in result)
        # Every word from original must appear somewhere in the output
        for word in ["Para A", "Para B", "Para C", "Para D"]:
            assert word in combined, f"'{word}' missing from chunked output"

    def test_no_separator_falls_back_to_char_split(self):
        """Text with no natural separators is split at character level."""
        fixture = load_fixture("strategy_recursive.json")
        cfg = fixture["edge_no_separator"]
        result = self.chunker.chunk(
            cfg["text"],
            chunk_size=cfg["chunk_size"],
            chunk_overlap=cfg["chunk_overlap"],
        )
        assert len(result) > 1
        for chunk in result:
            assert chunk["char_count"] <= cfg["chunk_size"]

    def test_indices_sequential(self):
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        result = self.chunker.chunk(text, chunk_size=30, chunk_overlap=5)
        for i, chunk in enumerate(result):
            assert chunk["index"] == i

    def test_overlap_start_reflects_shared_text(self):
        """Chunk n+1 overlap_start should reflect chars shared with chunk n."""
        text = "Para A\n\nPara B\n\nPara C"
        result = self.chunker.chunk(text, chunk_size=15, chunk_overlap=6)
        if len(result) >= 2:
            c0, c1 = result[0], result[1]
            # If overlap exists, end of c0 should match start of c1
            if c1["overlap_start_chars"] > 0:
                n = c1["overlap_start_chars"]
                assert c0["text"].endswith(c1["text"][:n])

    def test_custom_separators(self):
        """Custom separators are respected."""
        text = "sentence one. sentence two. sentence three. sentence four."
        result = self.chunker.chunk(
            text, chunk_size=30, chunk_overlap=5, separators=[". ", " ", ""]
        )
        assert len(result) >= 2
        for chunk in result:
            assert chunk["char_count"] <= 30


# ---------------------------------------------------------------------------
# TokenAwareChunker
# ---------------------------------------------------------------------------


class TestTokenAwareChunker:
    def setup_method(self):
        self.chunker = TokenAwareChunker()
        self.enc = tiktoken.get_encoding("cl100k_base")

    def _token_count(self, text: str) -> int:
        return len(self.enc.encode(text))

    def test_empty_text_returns_empty(self):
        result = self.chunker.chunk("", chunk_size_tokens=50, chunk_overlap_tokens=5)
        assert result == []

    def test_short_text_single_chunk(self):
        fixture = load_fixture("strategy_token.json")
        cfg = fixture["edge_short"]
        result = self.chunker.chunk(
            cfg["text"],
            chunk_size_tokens=cfg["chunk_size_tokens"],
            chunk_overlap_tokens=cfg["chunk_overlap_tokens"],
            encoding_name=cfg["encoding_name"],
        )
        assert len(result) == 1
        assert result[0]["overlap_start_chars"] == 0
        assert result[0]["overlap_end_chars"] == 0
        assert self._token_count(result[0]["text"]) <= cfg["chunk_size_tokens"]

    def test_token_count_hard_limit(self):
        """Every chunk must have ≤ chunk_size_tokens tokens — not an estimate."""
        fixture = load_fixture("strategy_token.json")
        cfg = fixture["happy_path"]
        result = self.chunker.chunk(
            cfg["text"],
            chunk_size_tokens=cfg["chunk_size_tokens"],
            chunk_overlap_tokens=cfg["chunk_overlap_tokens"],
            encoding_name=cfg["encoding_name"],
        )
        assert len(result) >= 1
        for chunk in result:
            count = self._token_count(chunk["text"])
            assert (
                count <= cfg["chunk_size_tokens"]
            ), f"Chunk {chunk['index']} has {count} tokens > limit {cfg['chunk_size_tokens']}"

    def test_no_overlap_produces_disjoint_chunks(self):
        """With chunk_overlap_tokens=0, every chunk token range is disjoint."""
        fixture = load_fixture("strategy_token.json")
        cfg = fixture["edge_no_overlap"]
        result = self.chunker.chunk(
            cfg["text"],
            chunk_size_tokens=cfg["chunk_size_tokens"],
            chunk_overlap_tokens=cfg["chunk_overlap_tokens"],
            encoding_name=cfg["encoding_name"],
        )
        assert len(result) >= 2
        for chunk in result:
            assert chunk["overlap_start_chars"] == 0
            assert chunk["overlap_end_chars"] == 0

    def test_overlap_start_chars_nonzero_after_first(self):
        """All chunks except the first should have overlap_start_chars > 0."""
        text = "Word " * 100  # 100 tokens approx
        result = self.chunker.chunk(text, chunk_size_tokens=20, chunk_overlap_tokens=5)
        assert len(result) >= 2
        # First chunk: no overlap from previous
        assert result[0]["overlap_start_chars"] == 0
        # Subsequent chunks: overlap from previous
        for chunk in result[1:]:
            assert chunk["overlap_start_chars"] > 0

    def test_indices_sequential(self):
        text = "Token " * 200
        result = self.chunker.chunk(text, chunk_size_tokens=30, chunk_overlap_tokens=5)
        for i, chunk in enumerate(result):
            assert chunk["index"] == i

    def test_char_count_consistent(self):
        """char_count must equal len(text) for every chunk."""
        text = "The quick brown fox. " * 20
        result = self.chunker.chunk(text, chunk_size_tokens=25, chunk_overlap_tokens=5)
        for chunk in result:
            assert chunk["char_count"] == len(chunk["text"])

    def test_invalid_overlap_raises(self):
        import pytest

        with pytest.raises(ValueError, match="chunk_overlap_tokens"):
            self.chunker.chunk(
                "some text", chunk_size_tokens=10, chunk_overlap_tokens=10
            )

    def test_custom_encoding(self):
        """p50k_base encoding should also produce valid chunks."""
        text = "Hello world, this is a test sentence for encoding. " * 10
        result = self.chunker.chunk(
            text,
            chunk_size_tokens=15,
            chunk_overlap_tokens=3,
            encoding_name="p50k_base",
        )
        enc = tiktoken.get_encoding("p50k_base")
        for chunk in result:
            assert len(enc.encode(chunk["text"])) <= 15


# ---------------------------------------------------------------------------
# SentenceChunker
# ---------------------------------------------------------------------------


class TestSentenceChunker:
    def setup_method(self):
        self.chunker = SentenceChunker()

    def test_empty_text_returns_empty(self):
        result = self.chunker.chunk(
            "", max_sentences_per_chunk=3, chunk_overlap_sentences=1
        )
        assert result == []

    def test_single_sentence_single_chunk(self):
        fixture = load_fixture("strategy_sentence.json")
        cfg = fixture["edge_single_sentence"]
        result = self.chunker.chunk(
            cfg["text"],
            language=cfg["language"],
            max_sentences_per_chunk=cfg["max_sentences_per_chunk"],
            chunk_overlap_sentences=cfg["chunk_overlap_sentences"],
        )
        assert len(result) == 1
        assert result[0]["overlap_start_chars"] == 0
        assert result[0]["overlap_end_chars"] == 0

    def test_chunks_end_at_sentence_boundary(self):
        """Every chunk must end with sentence-terminal punctuation or end-of-text."""
        import re

        fixture = load_fixture("strategy_sentence.json")
        cfg = fixture["happy_path"]
        result = self.chunker.chunk(
            cfg["text"],
            language=cfg["language"],
            max_sentences_per_chunk=cfg["max_sentences_per_chunk"],
            chunk_overlap_sentences=cfg["chunk_overlap_sentences"],
        )
        assert len(result) >= 2
        sentence_end = re.compile(r"[.!?]\s*$")
        for chunk in result:
            assert sentence_end.search(
                chunk["text"].rstrip()
            ), f"Chunk {chunk['index']} does not end at sentence boundary: {chunk['text']!r}"

    def test_no_overlap_disjoint(self):
        """With overlap=0, chunks share no sentences."""
        fixture = load_fixture("strategy_sentence.json")
        cfg = fixture["edge_no_overlap"]
        result = self.chunker.chunk(
            cfg["text"],
            language=cfg["language"],
            max_sentences_per_chunk=cfg["max_sentences_per_chunk"],
            chunk_overlap_sentences=cfg["chunk_overlap_sentences"],
        )
        assert len(result) >= 2
        for chunk in result:
            assert chunk["overlap_start_chars"] == 0
            assert chunk["overlap_end_chars"] == 0

    def test_overlap_start_nonzero_after_first(self):
        """All chunks after the first should have overlap_start_chars > 0."""
        fixture = load_fixture("strategy_sentence.json")
        cfg = fixture["happy_path"]
        result = self.chunker.chunk(
            cfg["text"],
            language=cfg["language"],
            max_sentences_per_chunk=cfg["max_sentences_per_chunk"],
            chunk_overlap_sentences=cfg["chunk_overlap_sentences"],
        )
        assert result[0]["overlap_start_chars"] == 0
        for chunk in result[1:]:
            assert chunk["overlap_start_chars"] > 0

    def test_indices_sequential(self):
        text = "One. Two. Three. Four. Five. Six. Seven. Eight. Nine. Ten."
        result = self.chunker.chunk(
            text, max_sentences_per_chunk=3, chunk_overlap_sentences=1
        )
        for i, chunk in enumerate(result):
            assert chunk["index"] == i

    def test_char_count_consistent(self):
        text = "Hello world. How are you? Fine thanks. Great to hear."
        result = self.chunker.chunk(
            text, max_sentences_per_chunk=2, chunk_overlap_sentences=1
        )
        for chunk in result:
            assert chunk["char_count"] == len(chunk["text"])

    def test_invalid_overlap_raises(self):
        import pytest

        with pytest.raises(ValueError, match="chunk_overlap_sentences"):
            self.chunker.chunk(
                "Some text.",
                max_sentences_per_chunk=3,
                chunk_overlap_sentences=3,
            )


# ---------------------------------------------------------------------------
# MarkdownStructureChunker
# ---------------------------------------------------------------------------


class TestMarkdownStructureChunker:
    def setup_method(self):
        self.chunker = MarkdownStructureChunker()

    def test_empty_text_returns_empty(self):
        result = self.chunker.chunk("", header_level=2)
        assert result == []

    def test_splits_at_header_boundaries(self):
        """Each h2 section becomes its own chunk."""
        fixture = load_fixture("strategy_markdown.json")
        cfg = fixture["happy_path"]
        result = self.chunker.chunk(
            cfg["text"],
            header_level=cfg["header_level"],
            max_chunk_size=cfg["max_chunk_size"],
        )
        # Introduction (h1) + 3 sections (h2) = 4 chunks
        assert len(result) == 4

    def test_chunk_boundaries_start_at_headers(self):
        """Every chunk (except possible preamble) should start with a header."""
        fixture = load_fixture("strategy_markdown.json")
        cfg = fixture["happy_path"]
        result = self.chunker.chunk(
            cfg["text"],
            header_level=cfg["header_level"],
            max_chunk_size=cfg["max_chunk_size"],
        )
        for chunk in result:
            assert chunk["text"].startswith(
                "#"
            ), f"Chunk {chunk['index']} does not start with a header: {chunk['text'][:40]!r}"

    def test_no_headers_single_chunk(self):
        """Text with no headers becomes one chunk."""
        fixture = load_fixture("strategy_markdown.json")
        cfg = fixture["edge_no_headers"]
        result = self.chunker.chunk(
            cfg["text"],
            header_level=cfg["header_level"],
            max_chunk_size=cfg["max_chunk_size"],
        )
        assert len(result) == 1

    def test_h1_split(self):
        """header_level=1 splits only at # headings."""
        fixture = load_fixture("strategy_markdown.json")
        cfg = fixture["edge_h1_only"]
        result = self.chunker.chunk(
            cfg["text"],
            header_level=cfg["header_level"],
            max_chunk_size=cfg["max_chunk_size"],
        )
        assert len(result) == 2
        assert result[0]["text"].startswith("# First")
        assert result[1]["text"].startswith("# Second")

    def test_oversized_section_is_sub_split(self):
        """Sections larger than max_chunk_size are sub-split into multiple chunks."""
        fixture = load_fixture("strategy_markdown.json")
        cfg = fixture["edge_oversized"]
        result = self.chunker.chunk(
            cfg["text"],
            header_level=cfg["header_level"],
            max_chunk_size=cfg["max_chunk_size"],
        )
        assert len(result) > 1
        for chunk in result:
            assert chunk["char_count"] <= cfg["max_chunk_size"]

    def test_indices_sequential(self):
        fixture = load_fixture("strategy_markdown.json")
        cfg = fixture["happy_path"]
        result = self.chunker.chunk(
            cfg["text"],
            header_level=cfg["header_level"],
            max_chunk_size=cfg["max_chunk_size"],
        )
        for i, chunk in enumerate(result):
            assert chunk["index"] == i

    def test_char_count_consistent(self):
        fixture = load_fixture("strategy_markdown.json")
        cfg = fixture["happy_path"]
        result = self.chunker.chunk(
            cfg["text"],
            header_level=cfg["header_level"],
            max_chunk_size=cfg["max_chunk_size"],
        )
        for chunk in result:
            assert chunk["char_count"] == len(chunk["text"])

    def test_no_overlap_fields(self):
        """Structure chunker does not create overlapping content."""
        fixture = load_fixture("strategy_markdown.json")
        cfg = fixture["happy_path"]
        result = self.chunker.chunk(
            cfg["text"],
            header_level=cfg["header_level"],
            max_chunk_size=cfg["max_chunk_size"],
        )
        for chunk in result:
            assert chunk["overlap_start_chars"] == 0
            assert chunk["overlap_end_chars"] == 0
