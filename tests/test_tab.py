"""Tests for the fretboard mapping and ASCII tab rendering.

These cover the pure-Python logic and do not require the heavy audio
dependencies (librosa, demucs, torch).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bass_tab.tab import (  # noqa: E402
    TUNINGS,
    Position,
    choose_position,
    notes_to_positions,
    render_tab,
)
from bass_tab.transcribe import Note  # noqa: E402


FOUR = TUNINGS[4]


def test_open_e_string():
    # MIDI 28 == open low E -> string 0, fret 0
    pos = choose_position(28, FOUR)
    assert pos == Position(string=0, fret=0)


def test_note_name():
    assert Note(midi=28, start=0, end=1).name == "E1"
    assert Note(midi=33, start=0, end=1).name == "A1"
    assert Note(midi=69, start=0, end=1).name == "A4"


def test_lowest_fret_preferred_without_history():
    # MIDI 33 is open A (string1 fret0) or 5th fret of E (string0 fret5).
    pos = choose_position(33, FOUR)
    assert pos == Position(string=1, fret=0)


def test_position_tracks_previous_hand():
    # Coming from fret 5, the 5th-fret A on the E string is closer than open A.
    prev = Position(string=0, fret=5)
    pos = choose_position(33, FOUR, prev=prev)
    assert pos.fret == 5 and pos.string == 0


def test_out_of_range_note_is_skipped():
    # MIDI 10 is far below the lowest open string.
    assert choose_position(10, FOUR) is None
    notes = [Note(midi=10, start=0, end=1), Note(midi=28, start=1, end=2)]
    placed = notes_to_positions(notes, FOUR)
    assert len(placed) == 1
    assert placed[0][1] == Position(string=0, fret=0)


def test_render_contains_all_strings_and_frets():
    notes = [
        Note(midi=28, start=0.0, end=0.5),   # E1, open E
        Note(midi=33, start=0.5, end=1.0),   # A1, open A
        Note(midi=43, start=1.0, end=1.5),   # G2, open G
    ]
    tab = render_tab(notes, FOUR, width=80, title="Test")
    assert "Test" in tab
    for label in ("E|", "A|", "D|", "G|"):
        assert label in tab
    # G string should be the top line, E the bottom line.
    lines = [l for l in tab.splitlines() if "|" in l]
    assert lines[0].startswith("G|")
    assert lines[-1].startswith("E|")


def test_render_empty():
    tab = render_tab([], FOUR)
    assert "no bass notes detected" in tab


def test_two_digit_fret_alignment():
    # MIDI 40 on the E string is fret 12; columns must stay aligned.
    notes = [Note(midi=40, start=0, end=0.5), Note(midi=28, start=0.5, end=1)]
    tab = render_tab(notes, FOUR)
    string_lines = [l for l in tab.splitlines() if l[:2] in ("G|", "D|", "A|", "E|")]
    body_lengths = {len(l) for l in string_lines}
    assert len(body_lengths) == 1  # all rows equal length -> aligned


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
