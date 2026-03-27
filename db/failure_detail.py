"""Format exceptions (including subprocess output) for persistence on failed jobs."""

import subprocess
import traceback


def format_failure(exc: BaseException) -> str:
    parts: list[str] = [f"{type(exc).__name__}: {exc}"]
    if isinstance(exc, subprocess.CalledProcessError):
        if exc.stderr and exc.stderr.strip():
            parts.append(f"--- stderr ---\n{exc.stderr.strip()}")
        if exc.stdout and exc.stdout.strip():
            parts.append(f"--- stdout ---\n{exc.stdout.strip()}")
    parts.append(f"--- traceback ---\n{traceback.format_exc()}")
    return "\n\n".join(parts)
