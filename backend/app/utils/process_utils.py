import subprocess
from typing import List, Tuple

def _exec_subprocess(cmd: List[str]) -> Tuple[int, str, str]:
    """
    Utility helper to execute subprocess commands cleanly without shell injection.
    """
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
