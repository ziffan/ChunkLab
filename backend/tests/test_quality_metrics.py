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

from backend.services.quality_metrics import (
    boundary_quality,
    information_density,
    is_complete,
)

# ---------------------------------------------------------------------------
# boundary_quality
# ---------------------------------------------------------------------------


class TestBoundaryQuality:
    def test_empty_returns_zero(self):
        assert boundary_quality("") == 0.0

    def test_full_score_sentence_end_uppercase_start(self):
        text = "This is a complete sentence."
        score = boundary_quality(text)
        assert score == 1.0

    def test_half_score_good_end_bad_start(self):
        # starts lowercase (bad start), ends with period (good end)
        text = "this ends with a period."
        score = boundary_quality(text)
        assert score == 0.5

    def test_half_score_good_start_bad_end(self):
        # starts uppercase (good start), ends mid-word (bad end)
        text = "Starts well but cut mid-wor"
        score = boundary_quality(text)
        assert score == 0.5

    def test_zero_score_bad_start_bad_end(self):
        text = "cut at both end"
        score = boundary_quality(text)
        assert score == 0.0

    def test_question_mark_end(self):
        assert boundary_quality("Is this complete?") == 1.0

    def test_exclamation_end(self):
        assert boundary_quality("Yes it is!") == 1.0

    def test_markdown_heading_start(self):
        text = "## Section Title\n\nContent here."
        assert boundary_quality(text) == 1.0

    def test_score_within_range(self):
        for text in ["", "abc", "Abc.", "abc.", "Abc"]:
            score = boundary_quality(text)
            assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# information_density
# ---------------------------------------------------------------------------


class TestInformationDensity:
    def test_empty_returns_zero(self):
        assert information_density("") == 0.0

    def test_no_whitespace(self):
        assert information_density("abcdef") == 1.0

    def test_all_whitespace(self):
        assert information_density("   \n\t  ") == 0.0

    def test_mixed(self):
        text = "ab cd"  # 5 chars, 1 space → 4/5 = 0.8
        assert information_density(text) == 0.8

    def test_range_zero_to_one(self):
        for text in ["", "hello world", "  a  ", "nospace"]:
            d = information_density(text)
            assert 0.0 <= d <= 1.0

    def test_dense_code_block(self):
        text = "x=1+2*3"
        assert information_density(text) == 1.0


# ---------------------------------------------------------------------------
# is_complete
# ---------------------------------------------------------------------------


class TestIsComplete:
    def test_empty_returns_true(self):
        assert is_complete("") is True

    def test_complete_sentence(self):
        assert is_complete("This is a sentence.") is True

    def test_ends_mid_word(self):
        assert is_complete("This ends mid-wor") is False

    def test_starts_lowercase(self):
        assert is_complete("starts mid sentence.") is False

    def test_both_bad(self):
        assert is_complete("cut on both sid") is False

    def test_uppercase_start_no_punct_end(self):
        assert is_complete("Hello world") is False

    def test_ends_with_closing_paren(self):
        assert is_complete("See note (1).") is True

    def test_ends_with_question(self):
        assert is_complete("Is this done?") is True

    def test_markdown_heading_complete(self):
        assert is_complete("## Section\n\nContent here.") is True
