import json
import uuid
import time
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Optional
from app.models.hook import HookAnalysisRequest, HookAnalysisResponse, HookCandidate, HookSensitivity
from app.services.studio.subtitle_service import SubtitleService, SubtitleSegment
from app.services.hooks.scene_analyzer import scene_analyzer
from app.services.hooks.audio_energy_analyzer import audio_energy_analyzer
from app.core.config import settings

logger = logging.getLogger("yt_splitter")

class HookEngine:
    """
    Smart Hook Detection Engine (AI Editorial Advisor):
    Multi-signal analysis combining Whisper transcripts, speech energy dynamics,
    visual scene cuts, and curiosity keyword triggers to suggest ranked hook timestamps.
    """
    def __init__(self, root_dir: Optional[Path] = None):
        if root_dir is None:
            root_dir = Path(__file__).resolve().parents[4]
        self.root_dir = root_dir
        self.config_path = self.root_dir / "assets" / "hooks" / "keywords.json"
        self.subtitle_service = SubtitleService()
        self.curiosity_keywords: List[str] = []
        self._load_keywords()

    def _load_keywords(self):
        if not self.config_path.exists():
            self.curiosity_keywords = ["wait", "watch this", "you won't believe", "here's why", "look at this"]
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.curiosity_keywords = [k.lower() for k in data.get("curiosity_phrases", [])]
        except Exception as e:
            logger.warning(f"Failed to load curiosity keywords: {e}")
            self.curiosity_keywords = ["wait", "watch this", "you won't believe", "here's why", "look at this"]

    async def analyze_hooks(self, request: HookAnalysisRequest) -> HookAnalysisResponse:
        start_t = time.time()
        video_path = Path(request.video_path).resolve()
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found at {video_path}")

        job_dir = settings.TEMP_DIR / "hooks" / str(uuid.uuid4())[:8]
        job_dir.mkdir(parents=True, exist_ok=True)

        max_sec = request.search_duration_seconds or 300.0

        # 1. Extract audio & transcribe
        wav_path = job_dir / "audio.wav"
        await self.subtitle_service.extract_audio(video_path, wav_path)
        segments = await self.subtitle_service.generate_subtitles(wav_path, model_size="tiny")

        # 2. Visual Scene Changes
        scene_times = await scene_analyzer.detect_scene_changes(video_path, threshold=0.3, max_seconds=max_sec)

        # 3. Audio Speech Energy
        energy_map = await audio_energy_analyzer.analyze_speech_energy(wav_path)

        # 4. Multi-Signal Scoring Engine
        candidates: List[HookCandidate] = []

        for idx, seg in enumerate(segments):
            if seg.start > max_sec:
                break

            # Filter dead air / ultra short segments
            if (seg.end - seg.start) < 0.8:
                continue

            sec_key = int(seg.start)
            seg_text_lower = seg.text.lower()

            reasons: List[str] = []
            score = 50.0  # Base confidence score

            # Signal 1: Curiosity Keyword Trigger
            matched_keyword = None
            for kw in self.curiosity_keywords:
                if kw in seg_text_lower:
                    matched_keyword = kw
                    break

            has_curiosity = False
            if matched_keyword:
                has_curiosity = True
                score += 25.0
                reasons.append(f"💡 Curiosity Hook ('{matched_keyword}')")

            # Signal 2: High Speech Energy Burst
            energy_val = energy_map.get(sec_key, 0.5)
            if energy_val > 0.7:
                score += 20.0
                reasons.append("🔥 High Speech Energy & Loudness Burst")
            elif energy_val > 0.5:
                score += 10.0

            # Signal 3: Visual Scene Transition Alignment
            has_scene = False
            for st in scene_times:
                if abs(st - seg.start) <= 2.5:
                    has_scene = True
                    score += 20.0
                    reasons.append("✂️ Visual Scene Cut Transition")
                    break

            # Signal 4: Emotional Punctuation / Urgency
            if "!" in seg.text or "?" in seg.text:
                score += 10.0
                reasons.append("❓ Question / Emotional Emphasis")

            # Cap confidence percentage
            final_confidence = min(99.0, round(score, 1))

            if final_confidence >= request.min_confidence:
                # Format timestamp e.g. 00:01:14
                hrs = int(seg.start // 3600)
                mins = int((seg.start % 3600) // 60)
                secs = int(seg.start % 60)
                formatted_ts = f"{hrs:02d}:{mins:02d}:{secs:02d}"

                if not reasons:
                    reasons.append("🎬 Engaging Segment Entry")

                candidates.append(HookCandidate(
                    id=f"hook_{idx:02d}",
                    timestamp=round(seg.start, 2),
                    timestamp_formatted=formatted_ts,
                    confidence=final_confidence,
                    reasons=reasons,
                    text_snippet=seg.text,
                    speech_energy=round(energy_val, 2),
                    has_scene_change=has_scene,
                    has_curiosity_phrase=has_curiosity
                ))

        # Rank candidates by confidence descending
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        top_candidates = candidates[:request.max_suggestions]

        duration = round(time.time() - start_t, 2)
        logger.info(f"[Hook Engine] Analyzed {video_path.name} in {duration}s -> Found {len(top_candidates)} hook candidates.")

        return HookAnalysisResponse(
            video_name=video_path.name,
            total_scene_changes=len(scene_times),
            candidates=top_candidates,
            processing_time_seconds=duration
        )

hook_engine = HookEngine()
