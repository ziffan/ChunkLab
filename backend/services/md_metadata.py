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

import re

_HEADER_RE = re.compile(r"^(#{1,6})\s+(.+?)$", re.MULTILINE)

MD_PATH_PATTERN_ID = "_md_path"


def extract_header_path(full_markdown: str, chunk_text: str) -> str:
    """Return 'H1 > H2 > H3' path for headers preceding chunk_text in full_markdown.

    Searches for chunk_text's position using progressively shorter anchors.
    Returns empty string when no headers precede the chunk.
    """
    if not full_markdown or not chunk_text:
        return ""

    headers = [
        (m.start(), len(m.group(1)), m.group(2).strip())
        for m in _HEADER_RE.finditer(full_markdown)
    ]
    if not headers:
        return ""

    stripped = chunk_text.strip()
    chunk_pos = -1
    for length in (80, 40, 20, 10):
        anchor = stripped[:length]
        if anchor:
            chunk_pos = full_markdown.find(anchor)
            if chunk_pos != -1:
                break

    if chunk_pos == -1:
        return ""

    stack: list[tuple[int, str]] = []
    for pos, level, title in headers:
        if pos >= chunk_pos:
            break
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))

    return " > ".join(title for _, title in stack)


def md_path_metadata(full_markdown: str, chunk_text: str) -> dict | None:
    """Return a metadata dict for _md_path, or None if no path exists."""
    path = extract_header_path(full_markdown, chunk_text)
    if not path:
        return None
    return {
        "pattern_id": MD_PATH_PATTERN_ID,
        "label": "md_path",
        "value": path,
    }
