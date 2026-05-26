"""Command-line interface for GIF Maker"""

import sys
import argparse

from .config import GIFConfig
from .creator import GIFCreator


def main():
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

    parser.add_argument('-f', '--file', required=True, type=str, help='Input video file')
    parser.add_argument('-s', '--start', default=0, type=int, help='Start time in seconds')
    parser.add_argument('-d', '--duration', default=5, type=int, help='Duration in seconds')
    parser.add_argument('-fp', '--fps', default=15, type=int, help='Frames per second')
    parser.add_argument('-sp', '--speedup', default=1.0, type=float, help='Speed multiplier')
    parser.add_argument('-r', '--resize', default=1.0, type=float, help='Resize factor')
    parser.add_argument('-t', '--text', default='', type=str, help='Text overlay')
    parser.add_argument('-p', '--position', default='center', type=str, 
                       help='Text position (center, top, bottom, top_left, etc.)')
    parser.add_argument('-fs', '--fontsize', default=50, type=int, help='Font size')
    parser.add_argument('-c', '--color', default='white', type=str, help='Text color')
    parser.add_argument('--loop', type=int, default=0, help='Loop count (0 = infinite)')
    parser.add_argument('-o', '--output', default='output.gif', type=str, help='Output filename')
    parser.add_argument('-m', '--method', default='two-pass', 
                       choices=['single-pass', 'two-pass'],
                       help='GIF creation method')
    parser.add_argument('--preview', action='store_true',
                       help='Preview the output before creating GIF')

    args = parser.parse_args()

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
        preview=args.preview
    )

    try:
        creator = GIFCreator(config)
        creator.create()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
