"""Download audio from a YouTube URL and convert it to WAV.

We call yt-dlp as a Python module (``python -m yt_dlp``) rather than relying on
a ``yt-dlp`` command being on the system PATH — this works as long as the
package is installed, which is friendlier for beginners. ffmpeg is located on
PATH if present, otherwise we fall back to the binary bundled with the
``imageio-ffmpeg`` package.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


class DownloadError(RuntimeError):
    """Raised when the audio could not be downloaded."""


def _ensure_yt_dlp() -> None:
    try:
        import yt_dlp  # noqa: F401
    except Exception as exc:  # not installed
        raise DownloadError(
            "The 'yt-dlp' package is not installed. Install it with "
            "`pip install yt-dlp` (or re-run setup_windows.bat)."
        ) from exc


def _find_ffmpeg() -> str | None:
    """Return a path to an ffmpeg binary, or None if none can be found."""
    on_path = shutil.which("ffmpeg")
    if on_path:
        return on_path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def download_audio(url: str, workdir: str | os.PathLike, *, quiet: bool = False) -> Path:
    """Download the best audio track for ``url`` and return the WAV path.

    Uses yt-dlp for the download and ffmpeg to extract a WAV file (PCM, the
    format the rest of the pipeline expects).
    """
    _ensure_yt_dlp()

    ffmpeg = _find_ffmpeg()
    if ffmpeg is None:
        raise DownloadError(
            "ffmpeg was not found. Install it (see SETUP_WINDOWS.md) or run "
            "`pip install imageio-ffmpeg` to use a bundled copy."
        )

    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    out_template = str(workdir / "source.%(ext)s")

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-x",                       # extract audio only
        "--audio-format", "wav",    # convert to wav via ffmpeg
        "--audio-quality", "0",     # best
        "--no-playlist",
        # Point yt-dlp at the ffmpeg we found (handles the bundled copy too).
        "--ffmpeg-location", ffmpeg,
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
