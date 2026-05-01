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

_END_BOUNDARY = re.compile(r'[.!?]["\')\]]*\s*$')
_START_BOUNDARY = re.compile(r'^[A-Z#\-\*>\d"\'(\[]')


def boundary_quality(text: str) -> float:
    """Score 0.0–1.0: +0.5 for sentence-boundary end, +0.5 for boundary start."""
    stripped = text.strip()
    if not stripped:
        return 0.0

    score = 0.0

    if _END_BOUNDARY.search(stripped) or text.rstrip().endswith("\n\n"):
        score += 0.5

    if _START_BOUNDARY.match(stripped):
        score += 0.5

    return round(score, 2)


def information_density(text: str) -> float:
    """Ratio of non-whitespace characters to total characters (0.0–1.0)."""
    if not text:
        return 0.0
    whitespace = sum(1 for c in text if c.isspace())
    return round((len(text) - whitespace) / len(text), 4)


def is_complete(text: str) -> bool:
    """False if the chunk appears cut mid-word at start or end."""
    stripped = text.strip()
    if not stripped:
        return True

    start_ok = not (stripped[0].isalpha() and stripped[0].islower())
    end_ok = not stripped[-1].isalnum()

    return start_ok and end_ok
