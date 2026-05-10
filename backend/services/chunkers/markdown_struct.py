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

import mistune

from .base import BaseChunker


class MarkdownStructureChunker(BaseChunker):
    """Split markdown by header boundaries using mistune AST parsing.

    Params:
        header_level (int): Split at headings of this level or above (default 2).
                            e.g. header_level=2 splits at # and ##.
        max_chunk_size (int): Character limit fallback for oversized sections (default 2000).

    Each chunk starts at a header boundary. The header is preserved as the
    first line of its chunk. Sections exceeding max_chunk_size are sub-split
    by characters (no overlap) as a fallback.
    """

    def chunk(self, text: str, **params) -> list[dict]:
        header_level: int = params.get("header_level", 2)
        max_chunk_size: int = params.get("max_chunk_size", 2000)

        if not text.strip():
            return []

        md = mistune.create_markdown(renderer="ast")
        ast_nodes = md(text)
        if not isinstance(ast_nodes, list) or not ast_nodes:
            return []

        sections = self._group_sections(ast_nodes, header_level)

        raw_chunks: list[str] = []
        for section_nodes in sections:
            section_text = self._ast_to_text(section_nodes).strip()
            if not section_text:
                continue
            if len(section_text) <= max_chunk_size:
                raw_chunks.append(section_text)
            else:
                # Fallback: character-based sub-split (no overlap, preserve header)
                header_line, _, body = section_text.partition("\n")
                body = body.strip()
                # Reserve chars for header + " (cont.)" + "\n\n" separator
                overhead = len(header_line) + len(" (cont.)") + 2
                step = max(1, max_chunk_size - overhead)
                start = 0
                first = True
                while start < len(body):
                    sub = body[start : start + step]
                    if first:
                        raw_chunks.append((header_line + "\n\n" + sub).strip())
                        first = False
                    else:
                        raw_chunks.append((header_line + " (cont.)\n\n" + sub).strip())
                    start += step

        result = []
        for i, chunk_text in enumerate(raw_chunks):
            result.append(
                {
                    "index": i,
                    "text": chunk_text,
                    "char_count": len(chunk_text),
                    "overlap_start_chars": 0,
                    "overlap_end_chars": 0,
                }
            )
        return result

    # ------------------------------------------------------------------
    # Section grouping
    # ------------------------------------------------------------------

    def _group_sections(self, nodes: list[dict], target_level: int) -> list[list[dict]]:
        """Group flat AST node list into sections.

        A new section starts whenever a heading of level <= target_level
        is encountered. blank_line nodes are skipped as section delimiters.
        """
        sections: list[list[dict]] = []
        current: list[dict] = []

        for node in nodes:
            if node.get("type") == "blank_line":
                continue
            if node.get("type") == "heading":
                level = (node.get("attrs") or {}).get("level", 0)
                if level <= target_level:
                    if current:
                        sections.append(current)
                    current = [node]
                    continue
            current.append(node)

        if current:
            sections.append(current)

        return sections if sections else [nodes]

    # ------------------------------------------------------------------
    # AST → markdown text reconstruction
    # ------------------------------------------------------------------

    def _ast_to_text(self, nodes: list[dict]) -> str:
        return "".join(self._node_to_text(n) for n in nodes)

    def _node_to_text(self, node: dict) -> str:  # noqa: PLR0911
        t = node.get("type", "")
        children: list[dict] = node.get("children") or []
        raw: str = node.get("raw", "")
        attrs: dict = node.get("attrs") or {}

        # Block nodes
        if t == "heading":
            level = attrs.get("level", 1)
            inner = "".join(self._node_to_text(c) for c in children).strip()
            return "#" * level + " " + inner + "\n\n"
        if t == "paragraph":
            inner = "".join(self._node_to_text(c) for c in children).strip()
            return inner + "\n\n"
        if t == "block_code":
            info = attrs.get("info", "") or ""
            return f"```{info}\n{raw}\n```\n\n"
        if t == "block_quote":
            inner = self._ast_to_text(children).strip()
            quoted = "\n".join("> " + line for line in inner.splitlines())
            return quoted + "\n\n"
        if t == "list":
            return "".join(self._node_to_text(c) for c in children) + "\n"
        if t == "list_item":
            inner = "".join(self._node_to_text(c) for c in children).strip()
            return "- " + inner + "\n"
        if t == "thematic_break":
            return "---\n\n"
        if t in ("blank_line", "block_html"):
            return raw + "\n" if raw else ""

        # Inline nodes
        if t == "text":
            return raw
        if t == "codespan":
            return f"`{raw}`"
        if t in ("softlinebreak", "linebreak"):
            return "\n"
        if t == "strong":
            inner = "".join(self._node_to_text(c) for c in children)
            return f"**{inner}**"
        if t == "emphasis":
            inner = "".join(self._node_to_text(c) for c in children)
            return f"*{inner}*"
        if t == "link":
            inner = "".join(self._node_to_text(c) for c in children)
            return f"[{inner}]({attrs.get('url', '')})"
        if t == "image":
            return f"![{attrs.get('alt', '')}]({attrs.get('url', '')})"
        if t == "html":
            return raw

        # Fallback
        if children:
            return "".join(self._node_to_text(c) for c in children)
        return raw
