# Professional YouTube Video Splitter Platform 🎬✂️

A modular, production-ready web application and REST/MCP API service that accepts YouTube video URLs, downloads authorized content using `yt-dlp`, extracts video metadata via `ffprobe`, splits videos into equal parts losslessly with `ffmpeg` stream copying (without re-encoding), and provides individual MP4 downloads plus a full `.ZIP` archive.

---

## 🌟 Highlights & Architecture

- **Lossless Stream Copying**: Uses `ffmpeg -c copy` for near-instant video segment extraction without video quality degradation or expensive re-encoding.
- **Service-Oriented Decoupled Architecture**:
  - `BaseDownloader` → `YouTubeDownloader` (ready for Google Drive, Dropbox, Local Uploads)
  - `BaseStorageProvider` → `LocalStorageProvider` (ready for AWS S3 / Cloudflare R2 / Supabase)
  - `FFmpegService` → Standalone video splitter engine
- **Model Context Protocol (MCP) Ready**: Built-in `/api/v1/mcp/tools` & `/api/v1/mcp/execute` endpoints allowing AI assistants (such as Claude) to split videos programmatically.
- **Auto-Cleanup**: Background periodic task automatically purges temporary downloaded files and clips after a configurable expiry time (default: 60 minutes).
- **Modern Dark UI**: Built with Next.js/React, TypeScript, Tailwind CSS, animated step progress timeline, duration counters, and link copy buttons.

---

## 📁 Repository Structure

```
Platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           ├── jobs.py          # Job creation, polling, & file downloads
│   │   │           └── mcp.py           # Model Context Protocol (MCP) API
│   │   ├── core/
│   │   │   ├── config.py                # Environment & safety settings
│   │   │   └── logging.py               # Structured logging
│   │   ├── models/
│   │   │   ├── job.py                   # Pydantic job models & status enums
│   │   │   └── video.py                 # Metadata & segment schemas
│   │   ├── services/
│   │   │   ├── download/                # yt-dlp YouTube downloader module
│   │   │   ├── metadata/                # ffprobe metadata module
│   │   │   ├── split/                   # Equal segment calculator
│   │   │   ├── processing/              # Lossless FFmpeg splitter
│   │   │   ├── storage/                 # Local filesystem storage (S3/R2 ready)
│   │   │   ├── zip/                     # ZIP archive service
│   │   │   └── jobs/                    # Pipeline manager & auto-cleanup
│   │   ├── utils/
│   │   │   ├── validators.py            # YouTube URL validation
│   │   │   └── ffmpeg_finder.py         # FFmpeg binary auto-resolver
│   │   └── main.py                      # FastAPI entrypoint
│   ├── tests/                           # Pytest test suite
│   ├── requirements.txt
│   └── temp/                            # Gitignored temporary job files
├── frontend/                            # React + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/                  # Header, JobForm, ProgressView, ResultsView, Footer
│   │   ├── services/                    # API communication client
│   │   └── types/                       # TypeScript interfaces
│   └── package.json
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Run Backend Server (FastAPI)

```bash
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Start FastAPI Uvicorn server on port 8000
python -m uvicorn app.main:app --reload --port 8000
```
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### 2. Run Frontend Web Interface (Vite / React / TS)

```bash
cd frontend

# Install dependencies if needed
npm install

# Start Vite dev server
npm run dev
```
- **Web App URL**: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Running Automated Tests

```bash
cd backend
venv\Scripts\pytest tests
```

---

## 🔌 Model Context Protocol (MCP) Integration

The backend exposes an MCP tool named `split_video`.

### MCP Tool Schema: `GET /api/v1/mcp/tools`
```json
{
  "tools": [
    {
      "name": "split_video",
      "description": "Downloads YouTube video, splits into equal parts losslessly, and creates ZIP archive.",
      "parameters": {
        "type": "object",
        "properties": {
          "url": { "type": "string" },
          "parts": { "type": "integer", "default": 4 },
          "quality": { "type": "string", "enum": ["best", "1080p", "720p", "audio_only"] }
        },
        "required": ["url"]
      }
    }
  ]
}
```

### Execution Endpoint: `POST /api/v1/mcp/execute`
```json
{
  "name": "split_video",
  "arguments": {
    "url": "https://www.youtube.com/watch?v=aqz-KE-bpKQ",
    "parts": 6,
    "quality": "best"
  }
}
```

---

## 🛡️ Security & Safety Rules

- **URL Validation**: Strict YouTube URL regex pattern matching.
- **Duration Limits**: Maximum video duration capped at 4 hours (configurable in `config.py`).
- **Part Range**: Segment count constrained between 2 and 50 parts.
- **Path Traversal Protection**: Sanitize all file download paths before serving local assets.
