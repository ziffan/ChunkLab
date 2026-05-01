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

import tiktoken

from .base import BaseChunker


class TokenAwareChunker(BaseChunker):
    """Encode text to tokens, split by exact token count, decode back to text.

    Guarantees every chunk contains ≤ chunk_size_tokens tokens — not an estimate.
    Params: chunk_size_tokens (int), chunk_overlap_tokens (int), encoding_name (str).
    """

    def chunk(self, text: str, **params) -> list[dict]:
        chunk_size_tokens: int = params.get("chunk_size_tokens", 256)
        chunk_overlap_tokens: int = params.get("chunk_overlap_tokens", 25)
        encoding_name: str = params.get("encoding_name", "cl100k_base")

        if chunk_overlap_tokens >= chunk_size_tokens:
            raise ValueError(
                f"chunk_overlap_tokens ({chunk_overlap_tokens}) must be less than "
                f"chunk_size_tokens ({chunk_size_tokens})"
            )

        if not text:
            return []

        enc = tiktoken.get_encoding(encoding_name)
        tokens = enc.encode(text)

        if not tokens:
            return []

        step = chunk_size_tokens - chunk_overlap_tokens
        chunks = []
        start = 0

        while start < len(tokens):
            end = min(start + chunk_size_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = enc.decode(chunk_tokens)

            # Overlap at start: first overlap_tokens tokens shared with previous chunk
            if start == 0:
                overlap_start_chars = 0
            else:
                ov_count = min(chunk_overlap_tokens, end - start)
                overlap_start_chars = len(enc.decode(tokens[start : start + ov_count]))

            # Overlap at end: last overlap_tokens tokens shared with next chunk
            next_start = start + step
            if next_start >= len(tokens):
                overlap_end_chars = 0
            else:
                ov_end_tokens = tokens[next_start:end]
                overlap_end_chars = (
                    len(enc.decode(ov_end_tokens)) if ov_end_tokens else 0
                )

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
