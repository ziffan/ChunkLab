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

from fastapi import APIRouter
from backend.models.requests import RegexTestRequest
from backend.models.responses import RegexTestResponse, RegexMatch, RegexError
from backend.services.metadata_extractor import validate_pattern

router = APIRouter()


@router.post("/regex/test", response_model=RegexTestResponse)
async def regex_test_endpoint(req: RegexTestRequest):
    is_valid, err_msg = validate_pattern(req.pattern)

    if not is_valid:
        return RegexTestResponse(
            is_valid=False,
            match_count=0,
            matches=[],
            truncated=False,
            error=RegexError(code="INVALID_REGEX", message=err_msg),
        )

    compiled = re.compile(req.pattern)
    all_matches = []
    for m in compiled.finditer(req.text):
        if compiled.groups > 0:
            value = m.group(1)
        else:
            value = m.group(0)
        all_matches.append(RegexMatch(value=value, start=m.start(), end=m.end()))

    truncated = len(all_matches) > 20
    matches = all_matches[:20]

    return RegexTestResponse(
        is_valid=True,
        match_count=len(all_matches),
        matches=matches,
        truncated=truncated,
        error=None,
    )
