import asyncio
import logging
from typing import List, Tuple

logger = logging.getLogger("yt_splitter")

def _exec_subprocess(cmd: List[str]) -> Tuple[int, str, str]:
    """
    Executes a subprocess command synchronously (meant to be run in a thread via asyncio.to_thread).
    Returns (returncode, stdout, stderr).
    """
    import subprocess
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        stdout, stderr = proc.communicate()
        return proc.returncode, stdout, stderr
    except Exception as e:
        logger.error(f"Failed to execute command '{' '.join(cmd)}': {e}")
        return 1, "", str(e)
