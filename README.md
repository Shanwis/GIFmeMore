# gifmemore

A command-line tool to quickly create high-quality animated GIFs from video files using FFmpeg. You can trim the video, adjust speed and FPS, resize the output, and add custom text overlays.

Now with two-pass encoding for superior quality!

## Features

* Preview your GIF before creating it with built-in ffplay integration
* Two-pass palette generation for better color quality and smaller file sizes
* Clip a specific segment from any video file
* Adjust the speed and frame rate (FPS) of the resulting GIF
* Resize the output to a specific scale (e.g., 50% of original size)
* Overlay custom text with control over size, color, and position
* Cross-platform support (Windows, macOS, Linux)
* Clean, modular codebase with proper abstraction

## Core Dependencies

This tool uses FFmpeg under the hood for video processing:
* **FFmpeg**: The industry-standard multimedia framework (must be installed on your system)
* **Python 3.7+**: For the command-line interface and orchestration

**Two-Pass Method:** By default, gifmemore generates a custom color palette first, then uses it to create the GIF. This produces significantly better quality than direct conversion, with optimized colors for your specific video content

## Installation

### 1. Install FFmpeg (if not already installed):
* **macOS:** `brew install ffmpeg`
* **Ubuntu/Debian:** `sudo apt install ffmpeg`
* **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### 2. Install gifmemore:
```bash
pip install gifmemore
```

## Usage

```bash
gifmemore -f <path_to_video> [options]
```

Or run as a module:
```bash
python -m gifmemore -f <path_to_video> [options]
```

### Examples

**Create a simple 5-second GIF from the beginning of a video:**
```bash
gifmemore -f "my_video.mp4" -d 5
```

**Create a high-quality GIF starting at 10 seconds, with red text at the top left:**
```bash
gifmemore -f "input.mp4" -s 10 -d 3 -fp 25 -t "Hello World!" -p top_left -c "red" -fs 70
```

**Create a half-sized GIF that runs at 1.5x speed:**
```bash
gifmemore -f "cool_movie.mkv" -s 65 -d 4 -r 0.5 -sp 1.5
```

**Use single-pass mode for faster (but lower quality) conversion:**
```bash
gifmemore -f "video.mp4" -m single-pass
```

**Preview before creating (recommended for fine-tuning):**
```bash
gifmemore -f "video.mp4" -s 10 -d 3 --preview
```

### All Options

```
usage: gifmemore [-h] -f FILE [-s START] [-d DURATION] [-fp FPS]
                 [-sp SPEEDUP] [-r RESIZE] [-t TEXT] [-p POSITION]
                 [-fs FONTSIZE] [-c COLOR] [--loop LOOP] [-o OUTPUT]
                 [-m {single-pass,two-pass}]

Create GIFs from video files using FFmpeg

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Input video file
  -s START, --start START
                        Start time in seconds (default: 0)
  -d DURATION, --duration DURATION
                        Duration in seconds (default: 5)
  -fp FPS, --fps FPS    Frames per second (default: 15)
  -sp SPEEDUP, --speedup SPEEDUP
                        Speed multiplier (default: 1.0)
  -r RESIZE, --resize RESIZE
                        Resize factor (default: 1.0)
  -t TEXT, --text TEXT  Text overlay
  -p POSITION, --position POSITION
                        Text position: center, top, bottom, top_left,
                        top_right, bottom_left, bottom_right (default: center)
  -fs FONTSIZE, --fontsize FONTSIZE
                        Font size (default: 50)
  -c COLOR, --color COLOR
                        Text color (default: white)
  --loop LOOP           Loop count, 0 = infinite (default: 0)
  -o OUTPUT, --output OUTPUT
                        Output filename (default: output.gif)
  -m METHOD, --method METHOD
                        GIF creation method: single-pass or two-pass (default: two-pass)
  --preview             Preview the output before creating GIF
```

## Programmatic Usage

You can also use gifmemore as a Python library:

```python
from gifmemore import GIFConfig, GIFCreator

config = GIFConfig(
    input_file="video.mp4",
    output_file="output.gif",
    start=10,
    duration=3,
    fps=20,
    method="two-pass",
    preview=True  # Enable preview
)

creator = GIFCreator(config)
creator.create()
```

## Preview Feature

The `--preview` flag opens the video segment in ffplay with all your filters applied (speed, resize, text, etc.) before creating the GIF. This lets you:

* See exactly what your GIF will look like
* Verify timing, text placement, and effects
* Adjust parameters without waiting for GIF creation
* Save time by getting it right the first time

After closing the preview window, you'll be prompted to continue or cancel the GIF creation.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
