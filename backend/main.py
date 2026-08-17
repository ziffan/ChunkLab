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

import logging
import multiprocessing
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.models.responses import HealthResponse
from backend.routers import chunk, models, regex, retrieve, tokenize

logger = logging.getLogger(__name__)

load_dotenv(os.path.join(os.getcwd(), ".env"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.services import retriever

    if retriever.is_available():
        try:
            retriever._get_model()
            logger.info("Retrieval model loaded: %s", retriever.MODEL_NAME)
        except Exception as e:  # noqa: BLE001
            logger.warning("Retrieval model warmup failed: %s", e)
    yield


app = FastAPI(title="ChunkLab API", version="1.0.0", lifespan=lifespan)

_raw = os.getenv("FRONTEND_ORIGIN", "").strip()
_cors_origins = (
    [o.strip() for o in _raw.split(",") if o.strip()]
    if _raw
    else ["http://localhost:5173", "http://127.0.0.1:5173"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chunk.router, prefix="/api")
app.include_router(tokenize.router, prefix="/api")
app.include_router(regex.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(retrieve.router, prefix="/api")


@app.get("/api/health", response_model=HealthResponse)
async def health():
    mock_mode = os.getenv("MOCK_MODE", "true").lower() == "true"
    return HealthResponse(status="ok", version="1.0.0", mock_mode=mock_mode)


if __name__ == "__main__":
    import uvicorn

    multiprocessing.freeze_support()
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run(app, host="127.0.0.1", port=port)
