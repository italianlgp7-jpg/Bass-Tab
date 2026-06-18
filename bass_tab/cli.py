"""Command-line interface for the bass tab generator."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .pipeline import generate_tab


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bass_tab",
        description="Generate a bass guitar tab from a YouTube link by "
        "isolating and transcribing the bass.",
    )
    parser.add_argument("url", help="YouTube URL of the song")
    parser.add_argument(
        "-o", "--output", metavar="FILE",
        help="write the tab to FILE instead of stdout",
    )
    parser.add_argument(
        "--strings", type=int, choices=(4, 5, 6), default=4,
        help="number of bass strings / tuning (default: 4)",
    )
    parser.add_argument(
        "--no-separate", dest="separate", action="store_false",
        help="skip Demucs bass isolation and transcribe the full mix",
    )
    parser.add_argument(
        "--keep-audio", action="store_true",
        help="keep the downloaded and isolated audio files",
    )
    parser.add_argument(
        "--width", type=int, default=80,
        help="characters per tab line before wrapping (default: 80)",
    )
    parser.add_argument(
        "--workdir", metavar="DIR",
        help="directory for temporary audio (default: a temp dir)",
    )
    parser.add_argument(
        "--title", help="title to print above the tab",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="suppress progress and tool output",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    def log(*a):
        if not args.quiet:
            print(*a, file=sys.stderr)

    try:
        tab = generate_tab(
            args.url,
            strings=args.strings,
            separate=args.separate,
            width=args.width,
            title=args.title,
            workdir=args.workdir,
            keep_audio=args.keep_audio,
            quiet=args.quiet,
            log=log,
        )
    except Exception as exc:  # surface a clean message, not a traceback
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(tab)
        log(f"✅  Tab written to {args.output}")
    else:
        print(tab)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
