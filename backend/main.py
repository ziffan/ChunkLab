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

import os
import sys
import multiprocessing

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Handle paths for PyInstaller frozen state
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Load .env relative to the executable or script
env_path = os.path.join(os.getcwd(), '.env')
if not os.path.exists(env_path):
    env_path = os.path.join(bundle_dir, '.env')
load_dotenv(env_path)

from backend.models.responses import HealthResponse
from backend.routers import chunk, tokenize, regex, models

app = FastAPI(title="ChunkLab API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local native app
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chunk.router, prefix="/api")
app.include_router(tokenize.router, prefix="/api")
app.include_router(regex.router, prefix="/api")
app.include_router(models.router, prefix="/api")


@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", version="1.0.0")


if __name__ == "__main__":
    import uvicorn
    # Required for pyinstaller --onefile multiprocessing issues
    multiprocessing.freeze_support()
    
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run(app, host="127.0.0.1", port=port)
