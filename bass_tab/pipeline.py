"""End-to-end pipeline: YouTube URL -> bass tab string."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from .download import download_audio
from .separate import isolate_bass, SeparationError
from .transcribe import transcribe_bass
from .tab import TUNINGS, render_tab


def generate_tab(
    url: str,
    *,
    strings: int = 4,
    separate: bool = True,
    width: int = 80,
    title: str | None = None,
    workdir: str | None = None,
    keep_audio: bool = False,
    quiet: bool = False,
    log=print,
) -> str:
    """Run the full pipeline and return the rendered bass tab.

    ``log`` is a callable used for progress messages (set to a no-op to silence).
    """
    if strings not in TUNINGS:
        raise ValueError(f"Unsupported string count {strings}; choose from {sorted(TUNINGS)}")
    tuning = TUNINGS[strings]

    owns_workdir = workdir is None
    work = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix="basstab_"))
    work.mkdir(parents=True, exist_ok=True)

    try:
        log(f"⬇️  Downloading audio from {url} ...")
        audio = download_audio(url, work, quiet=quiet)

        bass_audio = audio
        if separate:
            log("🎚️  Isolating bass with Demucs (this can take a while) ...")
            try:
                bass_audio = isolate_bass(audio, work, quiet=quiet)
            except SeparationError as exc:
                log(f"⚠️  {exc}\n    Falling back to the full mix.")
        else:
            log("ℹ️  Skipping separation; transcribing the full mix.")

        log("🎵  Detecting notes ...")
        notes = transcribe_bass(bass_audio)
        log(f"    Found {len(notes)} note events.")

        log("🪕  Building tab ...")
        return render_tab(notes, tuning, width=width, title=title)
    finally:
        if keep_audio:
            log(f"💾  Audio kept in {work}")
        elif owns_workdir:
            shutil.rmtree(work, ignore_errors=True)
