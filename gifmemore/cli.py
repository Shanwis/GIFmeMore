"""Command-line interface for GIF Maker"""

import sys
import json
import os
import argparse

from . import __version__
from .config import GIFConfig
from .creator import GIFCreator
from .presets import (
    get_default_config_path,
    create_default_config,
    load_config,
    resolve_config,
)

# Maps GIFConfig field names -> argparse dest names for the few that differ
CONFIG_TO_DEST = {
    "input_file": "file",
    "output_file": "output",
}


def main():
    # ── Stage 1: pre-parse config-related args ──────────────────────
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--config", type=str)
    pre_parser.add_argument("--preset", type=str)
    pre_parser.add_argument("--init", action="store_true")
    pre_parser.add_argument("-v","--version", action="store_true")
    pre_args, remaining = pre_parser.parse_known_args()
        
    if pre_args.version:
        print(f"gifmemore {__version__}")
        sys.exit(0)

    # --init: create config and exit
    if pre_args.init:
        path = pre_args.config if pre_args.config else get_default_config_path()
        create_default_config(path)
        print(f"Default configuration created at: {path}")
        sys.exit(0)

    # ── Stage 2: build main parser ───────────────────────────────────
    parser = argparse.ArgumentParser(
        description="Create GIFs from video files using FFmpeg",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Methods:
  single-pass: Faster, lower quality (direct conversion)
  two-pass:    Slower, higher quality (generates palette first) [default]

Examples:
  %(prog)s -f video.mp4
  %(prog)s -f video.mp4 -s 10 -d 3 -fp 20
  %(prog)s -f video.mp4 -m single-pass -t "Hello" -p top
        """
    )

    # Config args (redefined for --help visibility)
    parser.add_argument("--config", type=str,
                        help="Configuration file path")
    parser.add_argument("--preset", type=str,
                        help="Named preset from config file to apply")
    parser.add_argument("--init", action="store_true",
                        help="Create default configuration file and exit")

    # GIF creation args (original defaults preserved)
    parser.add_argument("-f", "--file", type=str, help="Input video file")
    parser.add_argument("-s", "--start", default=0, type=int,
                        help="Start time in seconds")
    parser.add_argument("-d", "--duration", default=5, type=int,
                        help="Duration in seconds")
    parser.add_argument("-fp", "--fps", default=15, type=int,
                        help="Frames per second")
    parser.add_argument("-sp", "--speedup", default=1.0, type=float,
                        help="Speed multiplier")
    parser.add_argument("-r", "--resize", default=1.0, type=float,
                        help="Resize factor")
    parser.add_argument("-t", "--text", default="", type=str,
                        help="Text overlay")
    parser.add_argument("-p", "--position", default="center", type=str,
                        help="Text position (center, top, bottom, "
                             "top_left, top_right, bottom_left, bottom_right)")
    parser.add_argument("-fs", "--fontsize", default=50, type=int,
                        help="Font size")
    parser.add_argument("-c", "--color", default="white", type=str,
                        help="Text color")
    parser.add_argument("--loop", type=int, default=0,
                        help="Loop count (0 = infinite)")
    parser.add_argument("-o", "--output", default="output.gif", type=str,
                        help="Output filename")
    parser.add_argument("-m", "--method", default="two-pass",
                        choices=["single-pass", "two-pass"],
                        help="GIF creation method")
    parser.add_argument("--preview", action="store_true",
                        help="Preview the output before creating GIF")

    # ── Stage 3: load config and inject as argparse defaults ────────
    explicit_config = pre_args.config is not None
    config_path = pre_args.config if explicit_config else get_default_config_path()

    if os.path.exists(config_path):
        try:
            data = load_config(config_path)
            config_dict = resolve_config(data, pre_args.preset)
            # Translate GIFConfig field names -> argparse dest names
            defaults = {
                CONFIG_TO_DEST.get(key, key): value
                for key, value in config_dict.items()
            }
            parser.set_defaults(**defaults)
        except KeyError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{config_path}': {e}",
                  file=sys.stderr)
            sys.exit(1)
    elif pre_args.preset:
        print(f"Error: Preset '{pre_args.preset}' specified "
              f"but config file not found at '{config_path}'.",
              file=sys.stderr)
        sys.exit(1)
    elif not explicit_config:
        # First run -- auto-create default config
        create_default_config(config_path)
        print(f"Default configuration created at: {config_path}")
    else:
        print(f"Error: Config file not found: {config_path}",
              file=sys.stderr)
        sys.exit(1)

    # ── Stage 4: full parse (CLI args override set_defaults) ────────
    args = parser.parse_args(remaining)

    if args.file is None:
        parser.error("Input file is required "
                      "(use -f or set 'input_file' in config)")

    config = GIFConfig(
        input_file=args.file,
        output_file=args.output,
        start=args.start,
        duration=args.duration,
        fps=args.fps,
        speedup=args.speedup,
        resize=args.resize,
        text=args.text,
        position=args.position,
        fontsize=args.fontsize,
        color=args.color,
        loop=args.loop,
        method=args.method,
        preview=args.preview,
    )

    try:
        creator = GIFCreator(config)
        creator.create()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
