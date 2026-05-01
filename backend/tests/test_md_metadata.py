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

from backend.services.md_metadata import extract_header_path, md_path_metadata

_DOC = """# Introduction

Intro content.

## Section One

Content for section one.

### Sub Topic

Sub topic content.

## Section Two

Content for section two.
"""


class TestExtractHeaderPath:
    def test_empty_inputs_return_empty(self):
        assert extract_header_path("", "anything") == ""
        assert extract_header_path("# Doc", "") == ""

    def test_no_headers_returns_empty(self):
        assert extract_header_path("plain text paragraph", "plain text") == ""

    def test_chunk_under_h1_only(self):
        path = extract_header_path(_DOC, "Intro content.")
        assert path == "Introduction"

    def test_chunk_under_h2(self):
        path = extract_header_path(_DOC, "Content for section one.")
        assert path == "Introduction > Section One"

    def test_chunk_under_h3(self):
        path = extract_header_path(_DOC, "Sub topic content.")
        assert path == "Introduction > Section One > Sub Topic"

    def test_chunk_under_second_h2(self):
        path = extract_header_path(_DOC, "Content for section two.")
        assert path == "Introduction > Section Two"

    def test_chunk_at_first_position_returns_empty(self):
        # chunk IS the first header line — nothing precedes it
        path = extract_header_path(_DOC, "# Introduction")
        assert path == ""

    def test_path_separator_is_arrow(self):
        path = extract_header_path(_DOC, "Content for section one.")
        assert " > " in path


class TestMdPathMetadata:
    def test_returns_none_when_no_headers(self):
        assert md_path_metadata("no headers here", "no headers") is None

    def test_returns_dict_with_correct_keys(self):
        item = md_path_metadata(_DOC, "Content for section one.")
        assert item is not None
        assert item["pattern_id"] == "_md_path"
        assert item["label"] == "md_path"
        assert "Introduction" in item["value"]

    def test_value_is_string(self):
        item = md_path_metadata(_DOC, "Sub topic content.")
        assert isinstance(item["value"], str)
