import shutil
import logging
from pathlib import Path

logger = logging.getLogger("yt_splitter")

def get_ffmpeg_executable() -> str:
    """Finds the ffmpeg executable path."""
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path
    
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_path and Path(ffmpeg_path).exists():
            return ffmpeg_path
    except ImportError:
        pass

    try:
        import static_ffmpeg
        ffmpeg_path, _ = static_ffmpeg.run.get_or_fetch_platform_executables_else_raise()
        if ffmpeg_path and Path(ffmpeg_path).exists():
            return ffmpeg_path
    except Exception:
        pass

    return "ffmpeg"

def get_ffprobe_executable() -> str:
    """Finds the ffprobe executable path."""
    ffprobe_path = shutil.which("ffprobe")
    if ffprobe_path:
        return ffprobe_path
    
    # Check if static_ffmpeg has ffprobe
    try:
        import static_ffmpeg
        _, ffprobe_path = static_ffmpeg.run.get_or_fetch_platform_executables_else_raise()
        if ffprobe_path and Path(ffprobe_path).exists():
            return ffprobe_path
    except Exception:
        pass

    ffmpeg_exe = get_ffmpeg_executable()
    if ffmpeg_exe and "ffmpeg" in ffmpeg_exe:
        possible_ffprobe = ffmpeg_exe.replace("ffmpeg", "ffprobe")
        if Path(possible_ffprobe).exists():
            return possible_ffprobe

    return "ffprobe"
