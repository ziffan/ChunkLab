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

def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[dict]:
    if len(text) == 0:
        return []

    step = chunk_size - chunk_overlap
    start = 0
    chunks = []

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        char_count = len(chunk)
        overlap_start = 0 if start == 0 else min(chunk_overlap, char_count)
        next_start = start + step
        overlap_end = 0
        if next_start < len(text):
            overlap_end = min(chunk_overlap, max(0, end - next_start))

        chunks.append({
            "index": len(chunks),
            "text": chunk,
            "char_count": char_count,
            "overlap_start_chars": overlap_start,
            "overlap_end_chars": overlap_end,
        })
        start = next_start

    return chunks
