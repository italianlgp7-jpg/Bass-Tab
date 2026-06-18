"""Download audio from a YouTube URL and convert it to WAV."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class DownloadError(RuntimeError):
    """Raised when the audio could not be downloaded."""


def _check_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise DownloadError(
            f"Required tool '{name}' was not found on your PATH. "
            "Install it and try again."
        )


def download_audio(url: str, workdir: str | os.PathLike, *, quiet: bool = False) -> Path:
    """Download the best audio track for ``url`` and return the WAV path.

    Uses ``yt-dlp`` for the download and lets it call ``ffmpeg`` to extract a
    WAV file (PCM, the format the rest of the pipeline expects).
    """
    _check_tool("yt-dlp")
    _check_tool("ffmpeg")

    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    out_template = str(workdir / "source.%(ext)s")

    cmd = [
        "yt-dlp",
        "-x",                       # extract audio only
        "--audio-format", "wav",    # convert to wav via ffmpeg
        "--audio-quality", "0",     # best
        "--no-playlist",
        "-o", out_template,
    ]
    if quiet:
        cmd.append("--quiet")
    cmd.append(url)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - network
        raise DownloadError(f"yt-dlp failed for {url!r}: {exc}") from exc

    wav = workdir / "source.wav"
    if not wav.exists():
        # yt-dlp may keep the original extension if conversion was skipped.
        candidates = sorted(workdir.glob("source.*"))
        if not candidates:
            raise DownloadError("Download finished but no audio file was produced.")
        wav = candidates[0]

    return wav
