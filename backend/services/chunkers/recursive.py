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

from .base import BaseChunker

DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


class RecursiveCharacterChunker(BaseChunker):
    """Split by progressively finer separators until chunks fit within chunk_size.

    Priority order: paragraph → line → sentence → word → character.
    Does not import LangChain; logic is a clean re-implementation.
    """

    def chunk(self, text: str, **params) -> list[dict]:
        chunk_size: int = params.get("chunk_size", 512)
        chunk_overlap: int = params.get("chunk_overlap", 50)
        separators: list[str] = list(params.get("separators", DEFAULT_SEPARATORS))

        if not text:
            return []

        texts = self._split_text(text, separators, chunk_size, chunk_overlap)

        result = []
        for i, t in enumerate(texts):
            prev_text = texts[i - 1] if i > 0 else ""
            next_text = texts[i + 1] if i < len(texts) - 1 else ""
            result.append(
                {
                    "index": i,
                    "text": t,
                    "char_count": len(t),
                    "overlap_start_chars": self._overlap_start(t, prev_text),
                    "overlap_end_chars": self._overlap_end(t, next_text),
                }
            )
        return result

    # ------------------------------------------------------------------
    # Core recursion
    # ------------------------------------------------------------------

    def _split_text(
        self, text: str, separators: list[str], chunk_size: int, chunk_overlap: int
    ) -> list[str]:
        final: list[str] = []

        # Pick the coarsest separator that actually appears in text
        separator = separators[-1] if separators else ""
        new_separators: list[str] = []
        for i, sep in enumerate(separators):
            if sep == "" or sep in text:
                separator = sep
                new_separators = separators[i + 1 :]
                break

        splits = self._split_by(text, separator)

        good: list[str] = []
        for s in splits:
            if len(s) <= chunk_size:
                good.append(s)
            else:
                if good:
                    final.extend(
                        self._merge(good, separator, chunk_size, chunk_overlap)
                    )
                    good = []
                if new_separators:
                    final.extend(
                        self._split_text(s, new_separators, chunk_size, chunk_overlap)
                    )
                else:
                    # No finer separator; emit as-is (unavoidably large chunk)
                    final.append(s)

        if good:
            final.extend(self._merge(good, separator, chunk_size, chunk_overlap))

        return final

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _split_by(self, text: str, separator: str) -> list[str]:
        if separator == "":
            return list(text)
        return [s for s in text.split(separator) if s]

    def _merge(
        self,
        splits: list[str],
        separator: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[str]:
        """Greedily merge small splits into chunks ≤ chunk_size with overlap.

        Two-phase trim after each output:
        1. Hard trim — remove leading splits until the next chunk fits ≤ chunk_size.
        2. Soft trim — remove leading splits until retained overlap ≤ chunk_overlap.
        """
        docs: list[str] = []
        current: list[str] = []
        sep_len = len(separator)

        def jlen(lst: list[str]) -> int:
            if not lst:
                return 0
            return sum(len(s) for s in lst) + sep_len * (len(lst) - 1)

        for s in splits:
            gap = sep_len if current else 0

            if jlen(current) + gap + len(s) > chunk_size and current:
                docs.append(separator.join(current))

                # Phase 1: ensure next chunk fits within chunk_size
                while current and jlen(current) + sep_len + len(s) > chunk_size:
                    if len(current) == 1:
                        current.clear()
                        break
                    current.pop(0)

                # Phase 2: trim excess overlap beyond chunk_overlap target
                while len(current) > 1 and jlen(current) > chunk_overlap:
                    current.pop(0)

            current.append(s)

        if current:
            docs.append(separator.join(current))

        return [d for d in docs if d.strip()]

    def _overlap_start(self, text: str, prev: str) -> int:
        """Chars at start of text that are shared with the end of prev."""
        if not prev:
            return 0
        limit = min(len(text), len(prev))
        for n in range(limit, 0, -1):
            if prev.endswith(text[:n]):
                return n
        return 0

    def _overlap_end(self, text: str, nxt: str) -> int:
        """Chars at end of text that are shared with the start of nxt."""
        if not nxt:
            return 0
        limit = min(len(text), len(nxt))
        for n in range(limit, 0, -1):
            if nxt.startswith(text[-n:]):
                return n
        return 0
