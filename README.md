<h1 align="center">gifmemore</h1>

<p align="center">
  <img src="https://raw.githubusercontent.com/Shanwis/gifmemore/main/assets/logo.png" width="256">
</p>

<p align="center">
  <a href="https://pypi.org/project/gifmemore/">
    <img src="https://img.shields.io/pypi/v/gifmemore" alt="PyPI version">
  </a>
  <a href="https://pepy.tech/project/gifmemore">
    <img src="https://pepy.tech/badge/gifmemore" alt="Downloads">
  </a>
  <a href="https://github.com/Shanwis/GIFmeMore/blob/main/LICENSE">
    <img src="https://img.shields.io/pypi/l/gifmemore" alt="License">
  </a>
  <a href="https://pypi.org/project/gifmemore/">
    <img src="https://img.shields.io/pypi/pyversions/gifmemore" alt="Python Versions">
  </a>
</p>
    
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
* Config file support with named presets for reusable parameter sets
* Input validation (empty file detection, ffprobe verification)
* Configurable palette statistics mode (`full`, `diff`, `single`) for optimal color quality
* Copy the resulting GIF directly to the system clipboard with `--clipboard` (cross-platform)
* Open the resulting GIF automatically after creation with `--open` (uses system default application)

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

**Create a GIF and copy it directly to the clipboard:**
```bash
gifmemore -f "video.mp4" -s 10 -d 3 --clipboard
```

**Create a GIF and open it automatically after creation:**
```bash
gifmemore -f "video.mp4" -s 10 -d 3 --open
```

**Use a named preset from your config file:**
```bash
gifmemore -f "video.mp4" --preset social_media
```

**Override individual preset values with CLI flags:**
```bash
gifmemore -f "video.mp4" --preset social_media -d 5 -fp 20
```

## Configuration & Presets

gifmemore supports a JSON configuration file for storing default values and reusable named presets.

### Config File Location

The config file path is platform-specific. On first run (without `--config`), a default config file is auto-created:

| Platform | Default Path |
|---|---|
| Linux | `~/.config/gifmemore/config.json` |
| macOS | `~/Library/Application Support/gifmemore/config.json` |
| Windows | `%APPDATA%\gifmemore\config.json` |

You can also specify an explicit path with `--config <path>`.

### Config File Format

```json
{
  "fps": 15,
  "loop": 0,
  "stats_mode": "diff",
  "presets": {
    "social_media": {
      "duration": 3,
      "fps": 20,
      "resize": 0.5,
      "text": "Hello World"
    },
    "quick_share": {
      "duration": 2,
      "fps": 10,
      "resize": 0.3,
      "method": "single-pass"
    }
  }
}
```

- **Top-level fields** act as defaults applied to every run.
- **`presets`** holds named profiles — enable one with `--preset <name>`.
- Preset values override top-level defaults; CLI flags override everything.

### Priority Order (lowest → highest)

1. `GIFConfig` code defaults
2. Config file top-level fields
3. Named preset fields
4. CLI arguments (always win)

### Commands

| Flag | Description |
|---|---|
| `--config <path>` | Use a specific config file (skips auto-creation) |
| `--preset <name>` | Apply a named preset from the config file |
| `--init` | Create or reset the default config file and exit |

### Examples

```bash
# First run — auto-creates config at platform path
gifmemore -f video.mp4

# Use a named preset
gifmemore -f video.mp4 --preset social_media

# Explicit config file with a preset
gifmemore --config my_projects.json --preset quick -f video.mp4

# Config provides input_file, no -f needed
gifmemore --config my_config.json

# Create/reset config
gifmemore --init

# Reset config at a custom path
gifmemore --init --config /path/to/config.json
```

### All Options

```
usage: gifmemore [-h] [--config CONFIG] [--preset PRESET] [--init]
                 [-f FILE] [-s START] [-d DURATION] [-fp FPS]
                 [-sp SPEEDUP] [-r RESIZE] [-t TEXT] [-p POSITION]
                 [-fs FONTSIZE] [-c COLOR] [--loop LOOP] [-o OUTPUT]
                 [-m {single-pass,two-pass}] [--preview]
                 [--stats-mode {full,diff,single}]

Create GIFs from video files using FFmpeg

options:
  -h, --help            show this help message and exit
  --config CONFIG       Configuration file path
  --preset PRESET       Named preset from config file to apply
  --init                Create default configuration file and exit
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
                        GIF creation method: single-pass or two-pass
                        (default: two-pass)
  --preview             Preview the output before creating GIF
  --clipboard           Copy the resulting GIF to the system clipboard
  --open                Open the GIF after creation using the system default
                        application
  --stats-mode STATS_MODE
                        Palette statistics mode: full, diff, or single
                        (default: diff)
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
    stats_mode="diff",
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
