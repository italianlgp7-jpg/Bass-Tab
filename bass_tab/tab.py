"""Map transcribed notes onto a bass fretboard and render ASCII tablature."""

from __future__ import annotations

from dataclasses import dataclass

from .transcribe import Note


@dataclass(frozen=True)
class Tuning:
    """A bass tuning, described by the open-string MIDI notes.

    Strings are listed low (thickest) to high (thinnest), e.g. E A D G.
    """

    name: str
    open_midi: tuple[int, ...]
    labels: tuple[str, ...]

    @property
    def n_strings(self) -> int:
        return len(self.open_midi)


# Standard tunings. MIDI: E1=28, A1=33, D2=38, G2=43, B0=23, C3=48.
TUNINGS: dict[int, Tuning] = {
    4: Tuning("4-string (E A D G)", (28, 33, 38, 43), ("E", "A", "D", "G")),
    5: Tuning("5-string (B E A D G)", (23, 28, 33, 38, 43), ("B", "E", "A", "D", "G")),
    6: Tuning("6-string (B E A D G C)", (23, 28, 33, 38, 43, 48),
              ("B", "E", "A", "D", "G", "C")),
}

MAX_FRET = 24


@dataclass(frozen=True)
class Position:
    """A fretboard position: which string (index, low->high) and fret."""

    string: int
    fret: int


def choose_position(
    midi: int,
    tuning: Tuning,
    *,
    prev: Position | None = None,
    max_fret: int = MAX_FRET,
) -> Position | None:
    """Pick a playable string/fret for ``midi``.

    Among all strings that can produce the note, prefer the one that keeps the
    fretting hand near its previous position; with no history, prefer the lowest
    fret number (and the thicker string on ties).
    """
    candidates: list[Position] = []
    for s, open_midi in enumerate(tuning.open_midi):
        fret = midi - open_midi
        if 0 <= fret <= max_fret:
            candidates.append(Position(string=s, fret=fret))

    if not candidates:
        return None

    if prev is None:
        return min(candidates, key=lambda p: (p.fret, -p.string))

    def cost(p: Position) -> tuple[float, int]:
        # Distance the hand has to travel, plus a small open-position bias.
        return (abs(p.fret - prev.fret) + 0.1 * p.fret, abs(p.string - prev.string))

    return min(candidates, key=cost)


def notes_to_positions(notes: list[Note], tuning: Tuning) -> list[tuple[Note, Position]]:
    """Map a sequence of notes to playable positions, keeping out-of-range ones out."""
    result: list[tuple[Note, Position]] = []
    prev: Position | None = None
    for note in notes:
        pos = choose_position(note.midi, tuning, prev=prev)
        if pos is None:
            continue  # outside the instrument's range; skip
        result.append((note, pos))
        prev = pos
    return result


def render_tab(
    notes: list[Note],
    tuning: Tuning,
    *,
    width: int = 80,
    title: str | None = None,
) -> str:
    """Render notes as a wrapped ASCII bass tab.

    Each note becomes one column; the fret number is written on its string and
    dashes fill the other strings. Columns are widened to fit two-digit frets.
    """
    placed = notes_to_positions(notes, tuning)
    n_strings = tuning.n_strings

    # Label column, e.g. "G|". Widest label decides the prefix width.
    label_w = max(len(lbl) for lbl in tuning.labels)
    prefix = [f"{lbl:>{label_w}}|" for lbl in tuning.labels]

    if not placed:
        body = "\n".join(p + "-" * 8 for p in reversed(prefix))
        header = (title + "\n\n") if title else ""
        return header + body + "\n\n(no bass notes detected)\n"

    # Build one cell (string) per note column.
    columns: list[list[str]] = []
    for _note, pos in placed:
        token = str(pos.fret)
        cell_w = len(token) + 1  # token followed by a dash separator
        col = []
        for s in range(n_strings):
            if s == pos.string:
                col.append(token + "-")
            else:
                col.append("-" * cell_w)
        columns.append(col)

    # Wrap columns into chunks that fit within `width` characters.
    avail = max(8, width - (label_w + 1))
    chunks: list[list[list[str]]] = []
    current: list[list[str]] = []
    used = 0
    for col in columns:
        cw = len(col[0])
        if current and used + cw > avail:
            chunks.append(current)
            current = []
            used = 0
        current.append(col)
        used += cw
    if current:
        chunks.append(current)

    lines: list[str] = []
    if title:
        lines.append(title)
        lines.append("")

    # Strings are rendered high (G) at the top, low (E) at the bottom.
    for ci, chunk in enumerate(chunks):
        for s in reversed(range(n_strings)):
            row = prefix[s] + "".join(col[s] for col in chunk) + "|"
            lines.append(row)
        if ci != len(chunks) - 1:
            lines.append("")  # blank line between systems

    return "\n".join(lines) + "\n"
