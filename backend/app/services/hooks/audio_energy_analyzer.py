import re
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from app.services.processing.ffmpeg_service import get_ffmpeg_executable
from app.utils.process_utils import _exec_subprocess

logger = logging.getLogger("yt_splitter")

class AudioEnergyAnalyzer:
    """
    Speech Energy & Loudness Dynamics Analyzer for Smart Hook Detection Engine:
    Detects sudden speech bursts, volume spikes, and emotional emphasis across timestamps.
    """
    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()

    async def analyze_speech_energy(self, audio_wav: Path, chunk_seconds: float = 1.0) -> Dict[int, float]:
        """
        Analyzes audio waveform and returns energy scores indexed by second timestamp.
        """
        if not audio_wav.exists():
            return {}

        cmd = [
            self.ffmpeg_bin, "-y",
            "-i", str(audio_wav),
            "-filter_complex", "astats=metadata=1:reset=1",
            "-f", "null", "-"
        ]

        returncode, stdout, stderr = await asyncio.to_thread(_exec_subprocess, cmd)
        energy_map: Dict[int, float] = {}

        if returncode == 0:
            # Extract RMS level or peak dB from stderr
            rms_matches = re.findall(r"pts_time:(\d+\.\d+).*?RMS level dB:\s*(-?\d+\.\d+)", stderr, re.DOTALL)
            for pts, dB in rms_matches:
                sec = int(float(pts))
                val = float(dB)
                # Convert dB (-60 to 0) to 0.0-1.0 scale
                norm_energy = max(0.0, min(1.0, (val + 60.0) / 60.0))
                energy_map[sec] = max(energy_map.get(sec, 0.0), norm_energy)

        logger.info(f"[Hook Engine] Analyzed audio energy for {len(energy_map)} second blocks")
        return energy_map

audio_energy_analyzer = AudioEnergyAnalyzer()
