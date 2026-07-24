#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for YouTube Video Splitter Platform.
Connects Claude Desktop and AI Assistants to the video processing engine.
"""

import sys
import json
import time
import urllib.request
import urllib.error

BACKEND_API_BASE = "http://localhost:8000/api/v1"

def http_post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def http_get(url: str) -> dict:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def handle_initialize(request_id):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "youtube-video-splitter-mcp",
                "version": "1.0.0"
            }
        }
    }

def handle_tools_list(request_id):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "tools": [
                {
                    "name": "split_video",
                    "description": "Downloads a YouTube video, extracts metadata via FFprobe, splits it losslessly into equal parts using FFmpeg stream copying, and returns downloadable clip URLs and a ZIP archive.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "Valid YouTube Video URL (e.g. https://www.youtube.com/watch?v=... or https://youtu.be/...)"
                            },
                            "parts": {
                                "type": "integer",
                                "description": "Number of equal parts to split video into (between 2 and 50)",
                                "default": 4
                            },
                            "quality": {
                                "type": "string",
                                "description": "Desired resolution quality: best, 1080p, 720p, or audio_only",
                                "enum": ["best", "1080p", "720p", "audio_only"],
                                "default": "best"
                            },
                            "channel": {
                                "type": "string",
                                "description": "Optional channel profile ID for intro/outro branding (e.g. rhymes4ever, cut_clips)"
                            }
                        },
                        "required": ["url"]
                    }
                }
            ]
        }
    }

def handle_tools_call(request_id, params):
    name = params.get("name")
    arguments = params.get("arguments", {})

    if name != "split_video":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Tool '{name}' not found"
            }
        }

    url = arguments.get("url")
    parts = arguments.get("parts", 4)
    quality = arguments.get("quality", "best")
    channel = arguments.get("channel")

    try:
        # 1. Create Job
        payload = {"url": url, "parts": parts, "quality": quality}
        if channel:
            payload["channel"] = channel

        create_res = http_post(f"{BACKEND_API_BASE}/jobs", payload)
        job_id = create_res["job_id"]

        # 2. Poll until completed or failed
        max_attempts = 120  # 2 minutes max polling
        attempts = 0
        status_res = create_res

        while attempts < max_attempts:
            time.sleep(2)
            attempts += 1
            status_res = http_get(f"{BACKEND_API_BASE}/jobs/{job_id}")
            current_status = status_res.get("status")

            if current_status == "completed":
                break
            elif current_status == "failed":
                error_msg = status_res.get("error", "Unknown error during video splitting")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Failed to split video {url}: {error_msg}"
                            }
                        ],
                        "isError": True
                    }
                }

        # 3. Get Download Links
        downloads_res = http_get(f"{BACKEND_API_BASE}/jobs/{job_id}/downloads")
        zip_url = downloads_res.get("zip_url", "")
        if zip_url and not zip_url.startswith("http"):
            zip_url = f"http://localhost:8000{zip_url}"

        clips = downloads_res.get("clips", [])
        meta = downloads_res.get("metadata") or {}

        # 4. Format Markdown Response for Claude
        lines = [
            f"### 🎬 Video Splitting Complete!",
            f"- **Source URL**: {url}",
            f"- **Job ID**: #{job_id}",
            f"- **Parts Generated**: {len(clips)} parts",
            f"- **Total Duration**: {meta.get('duration', 0):.1f} seconds",
            ""
        ]

        if zip_url:
            lines.append(f"📦 **[Download All Parts (.ZIP Archive)]({zip_url})**\n")

        lines.append("#### ✂️ Individual Video Clips:")
        for clip in clips:
            c_url = clip.get("download_url", "")
            if c_url and not c_url.startswith("http"):
                c_url = f"http://localhost:8000{c_url}"
            part_num = clip.get("part_number", 1)
            dur = clip.get("duration", 0)
            start = clip.get("start_time", 0)
            end = clip.get("end_time", 0)
            lines.append(f"- **Part {part_num:02d}** ({start:.1f}s → {end:.1f}s, {dur:.1f}s): [Download MP4]({c_url})")

        text_output = "\n".join(lines)

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": text_output
                    }
                ]
            }
        }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error connecting to video processing backend: {str(e)}"
                    }
                ],
                "isError": True
            }
        }

def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            msg = json.loads(line)
            req_id = msg.get("id")
            method = msg.get("method")
            params = msg.get("params", {})

            if method == "initialize":
                resp = handle_initialize(req_id)
            elif method == "notifications/initialized":
                continue
            elif method == "tools/list":
                resp = handle_tools_list(req_id)
            elif method == "tools/call":
                resp = handle_tools_call(req_id, params)
            elif method == "ping":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not supported"
                    }
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        except Exception as e:
            sys.stderr.write(f"MCP Server Error: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
