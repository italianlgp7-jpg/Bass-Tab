# 🎸 Bass Tab Generator

Generate a bass guitar tablature from a YouTube link. The tool downloads the
audio, **isolates the bass** from the rest of the mix using AI source
separation, detects the played notes, and renders a printable ASCII bass tab.

```
YouTube URL ──► download ──► isolate bass ──► detect notes ──► render tab
   (yt-dlp)        (demucs)        (librosa pyin)     (fretboard)
```

## Features

- 🎧 Downloads audio straight from a YouTube URL (`yt-dlp`).
- 🥁 Splits the song into stems and keeps **only the bass** (Demucs `htdemucs`).
- 🎵 Transcribes the monophonic bass line with a robust pitch tracker (pYIN).
- 🪕 Maps every note to a playable position on a 4‑string bass (EADG).
- 📄 Prints a clean, wrapped ASCII tab you can read or save to a file.

## Install

> 🔰 **New to all this / on Windows?** Follow the click-by-click guide in
> [SETUP_WINDOWS.md](SETUP_WINDOWS.md) — no coding required.

Requires Python 3.9+ and [`ffmpeg`](https://ffmpeg.org/) on your `PATH`.

```bash
pip install -r requirements.txt
```

> Demucs and PyTorch are large downloads. The first run will also fetch the
> pretrained separation model. If you skip Demucs (`--no-separate`) the tool
> falls back to transcribing the full mix, which is far less accurate.

## Usage

```bash
# Basic: print the tab to the terminal
python -m bass_tab "https://www.youtube.com/watch?v=XXXXXXXXXXX"

# Save the tab to a file and keep the isolated bass audio
python -m bass_tab "https://youtu.be/XXXXXXXXXXX" -o song.tab --keep-audio

# 5-string bass, faster (no separation)
python -m bass_tab "<url>" --strings 5 --no-separate
```

### Useful options

| Flag | Description |
| --- | --- |
| `-o, --output FILE` | Write the tab to a file instead of stdout. |
| `--strings {4,5,6}` | Number of bass strings / tuning to use (default 4). |
| `--no-separate` | Skip Demucs and transcribe the full mix. |
| `--keep-audio` | Keep the downloaded + isolated audio files. |
| `--width N` | Characters per tab line before wrapping (default 80). |
| `--workdir DIR` | Where to store temporary audio (default: a temp dir). |

## How it works

1. **Download** — `yt-dlp` grabs the best audio and `ffmpeg` converts it to WAV.
2. **Separate** — Demucs splits the track into `drums / bass / other / vocals`
   and we keep the `bass` stem so the transcriber only "hears" the bass.
3. **Transcribe** — librosa's pYIN estimates the fundamental frequency frame by
   frame; frames are quantized to semitones and grouped into note events.
4. **Tab** — each MIDI note is placed on the string/fret that keeps the hand in
   the lowest comfortable position, then rendered as ASCII.

## Limitations

- Best on clear, mostly-monophonic bass lines. Chords, heavy distortion and
  slides are approximated.
- Timing is shown by note ordering/spacing, not strict rhythmic notation.
- Separation quality depends on the mix.

## License

MIT — see [LICENSE](LICENSE).
