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

from fastapi import APIRouter, Query
from backend.services.model_detector import detect_models

router = APIRouter()


@router.get("/models")
async def list_models(
    provider: str = Query(..., description="Provider ID: ollama, lmstudio, openai, etc."),
    api_key: str | None = Query(None, description="Optional API key override"),
):
    return await detect_models(provider, api_key)
