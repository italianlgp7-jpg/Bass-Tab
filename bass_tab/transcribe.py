"""Transcribe an isolated bass recording into discrete note events.

The bass is (almost) monophonic, so we use librosa's pYIN fundamental-frequency
tracker, quantize each voiced frame to the nearest semitone, then merge runs of
identical semitones into note events.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np


# A bass realistically spans the low B of a 5-string (~31 Hz) up to the high
# frets of the G string (~400 Hz). We give pYIN a little headroom on both ends.
DEFAULT_FMIN = 30.0    # Hz  (~B0)
DEFAULT_FMAX = 500.0   # Hz  (~B4)


@dataclass(frozen=True)
class Note:
    """A single transcribed note event."""

    midi: int          # MIDI note number (rounded to a semitone)
    start: float       # seconds
    end: float         # seconds

    @property
    def duration(self) -> float:
        return self.end - self.start

    @property
    def name(self) -> str:
        names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = self.midi // 12 - 1
        return f"{names[self.midi % 12]}{octave}"


def transcribe_bass(
    audio_path: str | os.PathLike,
    *,
    sr: int = 22050,
    fmin: float = DEFAULT_FMIN,
    fmax: float = DEFAULT_FMAX,
    hop_length: int = 512,
    min_duration: float = 0.08,
    min_confidence: float = 0.5,
) -> list[Note]:
    """Return the list of :class:`Note` events detected in ``audio_path``.

    Parameters
    ----------
    sr:
        Sample rate to resample to. 22 kHz is plenty for bass frequencies and
        keeps pYIN fast.
    min_duration:
        Notes shorter than this (seconds) are discarded as transients/noise.
    min_confidence:
        Minimum mean voiced-probability for a frame run to count as a note.
    """
    import librosa  # imported lazily so `--help` works without the heavy deps

    y, sr = librosa.load(str(audio_path), sr=sr, mono=True)
    if y.size == 0:
        return []

    f0, voiced_flag, voiced_prob = librosa.pyin(
        y,
        fmin=fmin,
        fmax=fmax,
        sr=sr,
        hop_length=hop_length,
    )

    times = librosa.times_like(f0, sr=sr, hop_length=hop_length)

    # Quantize each voiced frame to the nearest MIDI semitone.
    midi = np.full(f0.shape, -1, dtype=int)
    voiced = voiced_flag & ~np.isnan(f0)
    midi[voiced] = np.round(librosa.hz_to_midi(f0[voiced])).astype(int)

    frame_dt = hop_length / sr
    notes = _segment(midi, voiced_prob, times, frame_dt, min_duration, min_confidence)
    return notes


def _segment(
    midi: np.ndarray,
    voiced_prob: np.ndarray,
    times: np.ndarray,
    frame_dt: float,
    min_duration: float,
    min_confidence: float,
) -> list[Note]:
    """Merge consecutive frames with the same MIDI value into note events."""
    notes: list[Note] = []
    n = len(midi)
    i = 0
    while i < n:
        if midi[i] < 0:
            i += 1
            continue
        j = i
        while j + 1 < n and midi[j + 1] == midi[i]:
            j += 1

        start = float(times[i])
        end = float(times[j] + frame_dt)
        confidence = float(np.nanmean(voiced_prob[i : j + 1]))

        if end - start >= min_duration and confidence >= min_confidence:
            notes.append(Note(midi=int(midi[i]), start=start, end=end))
        i = j + 1

    return notes
