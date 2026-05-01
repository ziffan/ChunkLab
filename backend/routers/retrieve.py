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

from fastapi import APIRouter
from fastapi.responses import JSONResponse

import backend.services.retriever as retriever_svc
from backend.models.requests import RetrieveRequest
from backend.models.responses import RetrieveResponse, RetrieveResult

router = APIRouter()

_UNAVAILABLE_BODY = {
    "error": "RETRIEVAL_UNAVAILABLE",
    "message": "Install retrieval extras: pip install -r requirements-retrieval.txt",
}


@router.post("/retrieve")
async def retrieve_endpoint(req: RetrieveRequest):
    if not retriever_svc.is_available():
        return JSONResponse(status_code=503, content=_UNAVAILABLE_BODY)

    try:
        raw = retriever_svc.retrieve(
            req.query,
            [c.model_dump() for c in req.chunks],
            req.top_k,
        )
    except ImportError:
        return JSONResponse(status_code=503, content=_UNAVAILABLE_BODY)

    return RetrieveResponse(
        results=[RetrieveResult(**r) for r in raw],
        model_used=retriever_svc.MODEL_NAME,
        is_available=True,
    )
