# ChunkLab

Browser-based developer sandbox for testing and validating text chunking pipeline configurations.

## Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate       # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Usage

- Backend runs on `http://localhost:8000`
- Frontend runs on `http://localhost:5173`
- API proxy is configured in `vite.config.js` to forward `/api` requests to the backend
