import logging
from pathlib import Path
from typing import Optional
from app.services.processing.ffmpeg_service import get_ffmpeg_executable

logger = logging.getLogger("yt_splitter")

class AudioProcessingService:
    """
    Audio Processing Engine for Creator Studio:
    - EBU R128 Loudness Normalization (-16 LUFS for Shorts/Reels, -24 LUFS for Standard)
    - Subtle Pitch Control (-3.0 to +3.0 semitones)
    - Peak Limiter & Audio Compressor
    """
    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()

    def get_audio_filter_graph(
        self,
        normalize: bool = True,
        target_lufs: float = -16.0,
        pitch_semitones: float = 0.0
    ) -> Optional[str]:
        filters = []

        # 1. Pitch adjustment filter (semitones to frequency ratio)
        if pitch_semitones != 0.0:
            # 1 semitone = 2^(1/12) ~ 1.059463
            ratio = 2.0 ** (pitch_semitones / 12.0)
            sample_rate = int(44100 * ratio)
            filters.append(f"asetrate={sample_rate},aresample=44100,atempo={1.0/ratio:.4f}")

        # 2. Loudness normalization (EBU R128 standard)
        if normalize:
            # target_lufs e.g. -16.0 for web shorts, -24.0 for standard broadcast
            filters.append(f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11")

        # 3. Final limiter to ensure zero audio clipping
        filters.append("alimiter=limit=0.95")

        if filters:
            return ",".join(filters)
        return None
