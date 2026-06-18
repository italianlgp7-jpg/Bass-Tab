"""Isolate the bass stem from a full mix using Demucs."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


class SeparationError(RuntimeError):
    """Raised when bass separation fails."""


def _demucs_available() -> bool:
    try:
        import demucs  # noqa: F401
    except Exception:
        return False
    return True


def isolate_bass(
    audio_path: str | os.PathLike,
    workdir: str | os.PathLike,
    *,
    model: str = "htdemucs",
    quiet: bool = False,
) -> Path:
    """Run Demucs on ``audio_path`` and return the path to the bass stem.

    Demucs writes stems to ``<workdir>/<model>/<track-name>/bass.wav``. We ask
    it for only the bass stem (``--two-stems`` would mix everything else into
    "no_bass", so we instead select the bass stem from the full split).
    """
    if not _demucs_available():
        raise SeparationError(
            "Demucs is not installed. Install it with `pip install demucs` "
            "or run with --no-separate to transcribe the full mix."
        )

    audio_path = Path(audio_path)
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "demucs",
        "-n", model,
        "--two-stems", "bass",   # split into "bass" and "no_bass" (faster)
        "-o", str(workdir),
        str(audio_path),
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL if quiet else None,
            stderr=subprocess.STDOUT if quiet else None,
        )
    except subprocess.CalledProcessError as exc:
        raise SeparationError(f"Demucs failed: {exc}") from exc

    stem = workdir / model / audio_path.stem / "bass.wav"
    if not stem.exists():
        raise SeparationError(f"Expected bass stem not found at {stem}")
    return stem
