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


def extract_metadata_from_compiled(
    text: str, compiled_patterns: list[tuple[dict, re.Pattern]]
) -> list[dict]:
    metadata_list = []

    for p, compiled in compiled_patterns:
        if compiled.groups > 0:
            for m in compiled.finditer(text):
                val = m.group(1)
                if val is not None:
                    metadata_list.append(
                        {
                            "pattern_id": p["id"],
                            "label": p["label"],
                            "value": str(val),
                        }
                    )
        else:
            for m in compiled.finditer(text):
                metadata_list.append(
                    {
                        "pattern_id": p["id"],
                        "label": p["label"],
                        "value": str(m.group(0)),
                    }
                )

    return metadata_list


def extract_metadata(text: str, patterns: list[dict]) -> tuple[list[dict], dict | None]:
    # Legacy wrapper or for single calls
    compiled_patterns = []
    for p in patterns:
        try:
            compiled = re.compile(p["pattern"])
            compiled_patterns.append((p, compiled))
        except re.error as e:
            return (
                [],
                {
                    "code": "INVALID_REGEX",
                    "message": f"Pattern '{p['pattern']}' is invalid: {e}",
                    "pattern_id": p["id"],
                },
            )

    return (extract_metadata_from_compiled(text, compiled_patterns), None)


def validate_pattern(pattern: str) -> tuple[bool, str | None]:
    try:
        re.compile(pattern)
        return (True, None)
    except re.error as e:
        return (False, str(e))
