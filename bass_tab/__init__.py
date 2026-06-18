"""Generate bass guitar tablature from a YouTube link.

The package is organised as a small pipeline:

    download  -> separate -> transcribe -> tab

Each stage lives in its own module and can be used on its own.
"""

from .transcribe import Note, transcribe_bass
from .tab import Tuning, TUNINGS, render_tab

__all__ = [
    "Note",
    "transcribe_bass",
    "Tuning",
    "TUNINGS",
    "render_tab",
    "__version__",
]

__version__ = "0.1.0"
