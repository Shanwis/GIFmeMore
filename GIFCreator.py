import os
import sys
import subprocess
from datetime import datetime
import argparse

def main():
    parser = argparse.ArgumentParser(description="Make video into GIFS (FFmpeg version)")

    parser.add_argument('-f', '--file', required=True, type=str)
    parser.add_argument('-s', '--start', default=0, type=int)
    parser.add_argument('-d', '--duration', default=5, type=int)
    parser.add_argument('-fp', '--fps', default=15, type=int)
    parser.add_argument('-sp','--speedup', default=1.0,type=float)
    parser.add_argument('-r', '--resize', default=1.0,type=float)
    parser.add_argument('-t', '--text', default='', type=str)
    parser.add_argument('-p', '--position', default='center', type=str)
    parser.add_argument('-fs', '--fontsize', default=50, type=int)
    parser.add_argument('-c', '--color', default='white', type=str)
    parser.add_argument('--loop', type=int, default=0)
    parser.add_argument('-o', '--output', default='output.gif', type=str)

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print("File not found")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output == "output.gif":
        args.output = f"output_{timestamp}.gif"

    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", args.output)

    # Position mapping
    pos_map = {
        "top_left": "10:10",
        "top_right": "W-tw-10:10",
        "bottom_left": "10:H-th-10",
        "bottom_right": "W-tw-10:H-th-10",
        "center": "(W-tw)/2:(H-th)/2",
        "top": "(W-tw)/2:10",
        "bottom": "(W-tw)/2:H-th-10"
    }
    pos = pos_map.get(args.position, "(W-tw)/2:(H-th)/2")

    # Filters
    filters = []

    # Speed (setpts)
    if args.speedup != 1.0:
        filters.append(f"setpts={1/args.speedup}*PTS")

    # Resize
    if args.resize != 1.0:
        filters.append(f"scale=iw*{args.resize}:ih*{args.resize}")

    # FPS
    filters.append(f"fps={args.fps}")

    # Text overlay
    if args.text:
        drawtext = (
            f"drawtext=text='{args.text}':"
            f"fontcolor={args.color}:"
            f"fontsize={args.fontsize}:"
            f"x={pos.split(':')[0]}:y={pos.split(':')[1]}"
        )
        filters.append(drawtext)

    filter_chain = ",".join(filters)

    # Loop handling
    loop_flag = f"-loop {args.loop}" if args.loop >= 0 else ""

    cmd = [
        "ffmpeg",
        "-ss", str(args.start),
        "-t", str(args.duration),
        "-i", args.file,
        "-vf", filter_chain,
        "-y",
        output_path
    ]

    print("Running FFmpeg command:")
    print(" ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
        print(f"GIF created at {output_path}")
    except subprocess.CalledProcessError:
        print("FFmpeg failed")
        sys.exit(1)

if __name__ == "__main__":
    main()