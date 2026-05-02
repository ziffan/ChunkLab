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

import pysbd

from .base import BaseChunker

_SUPPORTED_LANGUAGES = {
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


class SentenceChunker(BaseChunker):
    """Group sentences into chunks using pysbd sentence boundary detection.

    .. deprecated::
        Use ``IndonesianSentenceSplitter`` (strategy ``"sentence_id"``) for Bahasa Indonesia.
        This chunker supports only the 23 pysbd languages listed in ``_SUPPORTED_LANGUAGES``.

    Params:
        language (str): pysbd language code, default "en".
        max_sentences_per_chunk (int): max sentences per chunk, default 5.
        chunk_overlap_sentences (int): sentences to repeat at start of next chunk, default 1.

    Every chunk ends at a sentence boundary.
    """

    def chunk(self, text: str, **params) -> list[dict]:
        language: str = params.get("language", "en")
        max_sents: int = params.get("max_sentences_per_chunk", 5)
        overlap_sents: int = params.get("chunk_overlap_sentences", 1)

        if language not in _SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{language}'. "
                f"Supported codes: {sorted(_SUPPORTED_LANGUAGES)}"
            )

        if overlap_sents >= max_sents:
            raise ValueError(
                f"chunk_overlap_sentences ({overlap_sents}) must be less than "
                f"max_sentences_per_chunk ({max_sents})"
            )

        if not text:
            return []

        segmenter = pysbd.Segmenter(language=language, clean=False)
        sentences = [s for s in segmenter.segment(text) if s.strip()]

        if not sentences:
            return []

        step = max_sents - overlap_sents
        chunks: list[dict] = []
        start = 0

        while start < len(sentences):
            end = min(start + max_sents, len(sentences))
            group = sentences[start:end]
            chunk_text = "".join(group)

            # overlap_start: first overlap_sents sentences (shared with previous chunk)
            if start == 0:
                overlap_start_chars = 0
            else:
                ov_count = min(overlap_sents, end - start)
                overlap_start_chars = sum(len(s) for s in group[:ov_count])

            # overlap_end: last overlap_sents sentences (shared with next chunk)
            next_start = start + step
            if next_start >= len(sentences):
                overlap_end_chars = 0
            else:
                ov_end_sents = group[max(0, len(group) - overlap_sents) :]
                overlap_end_chars = sum(len(s) for s in ov_end_sents)

            chunks.append(
                {
                    "index": len(chunks),
                    "text": chunk_text,
                    "char_count": len(chunk_text),
                    "overlap_start_chars": overlap_start_chars,
                    "overlap_end_chars": overlap_end_chars,
                }
            )
            start = next_start

        return chunks
