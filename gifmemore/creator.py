"""GIF creation engine"""

import json
import os
import platform
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import List

from .config import GIFConfig
from .filters import FilterBuilder
from .clipboard import copy_gif_to_clipboard


class GIFCreator:
    """Creates GIFs from video files using FFmpeg"""
    
    def __init__(self, config: GIFConfig):
        self._check_ffmpeg()
        self.config = config
        self._validate_input()
        self._prepare_output()
    
    @staticmethod
    def _check_ffmpeg():
        """Verify FFmpeg is installed and available on PATH"""
        if shutil.which("ffmpeg") is None:
            raise RuntimeError(
                "FFmpeg is required but not found on your system.\n"
                "Install it via:\n"
                "  macOS: brew install ffmpeg\n"
                "  Ubuntu/Debian: sudo apt install ffmpeg\n"
                "  Windows: https://ffmpeg.org/download.html"
            )
    
    def _validate_input(self):
        """Validate input file exists and is a valid video file"""
        if not os.path.exists(self.config.input_file):
            raise FileNotFoundError(f"Input file not found: {self.config.input_file}")

        if os.path.getsize(self.config.input_file) == 0:
            raise ValueError(f"Input file is empty: {self.config.input_file}")

        ffprobe = shutil.which("ffprobe")
        if ffprobe:
            try:
                result = subprocess.run(
                    [ffprobe, "-v", "quiet", "-print_format", "json",
                     "-show_streams", self.config.input_file],
                    capture_output=True, text=True, check=True
                )
                info = json.loads(result.stdout)
                if not any(s.get("codec_type") == "video" for s in info.get("streams", [])):
                    raise ValueError(
                        f"No video streams found in: {self.config.input_file}"
                    )
            except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
                raise ValueError(
                    f"Unable to read video file: {self.config.input_file} ({e})"
                )
    
    def _prepare_output(self):
        """Prepare output directory and filename"""
        self.config.output_file = os.path.expanduser(self.config.output_file)
        out_dir = os.path.dirname(self.config.output_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            self.output_path = self.config.output_file
        else:
            if self.config.output_file == "output.gif":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.config.output_file = f"output_{timestamp}.gif"
            self.output_path = self.config.output_file
    
    def _open_gif(self):
        """Open the GIF using the system's default application"""
        path = os.path.abspath(self.output_path)
        system = platform.system()

        if system == "Darwin":
            subprocess.run(["open", path], check=False)
        elif system == "Windows":
            os.startfile(path)
        elif system == "Linux":
            opener = shutil.which("xdg-open")
            if opener:
                subprocess.run([opener, path], check=False)
            else:
                print("Warning: xdg-open not found. Install xdg-utils to use --open.")
        else:
            print(f"Warning: Cannot open files on {system}")

    def _build_filter_chain(self) -> str:
        """Build the FFmpeg filter chain"""
        return (FilterBuilder(self.config)
                .add_speed_filter()
                .add_resize_filter()
                .add_fps_filter()
                .add_text_filter()
                .build())
    
    def _run_command(self, cmd: List[str], description: str = "FFmpeg"):
        """Execute FFmpeg command"""
        print(f"Running {description} command:")
        print(" ".join(cmd))
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"\n{description} failed!")
            print(f"Error output:\n{e.stderr}")
            raise
    
    def create_single_pass(self):
        """Create GIF using single-pass method (faster, lower quality)"""
        filter_chain = self._build_filter_chain()
        
        cmd = [
            "ffmpeg",
            "-ss", str(self.config.start),
            "-t", str(self.config.duration),
            "-i", self.config.input_file,
            "-vf", filter_chain,
            "-y",
            "-loop", str(self.config.loop),
            self.output_path
        ]
        
        self._run_command(cmd, "Single-pass")
        print(f"✓ GIF created at {self.output_path}")
        if self.config.clipboard:
            copy_gif_to_clipboard(self.output_path)
        if self.config.open_gif:
            self._open_gif()

    def create_two_pass(self):
        """Create GIF using two-pass method (slower, higher quality)
        
        This method generates a custom palette first, then uses it to create
        the GIF, resulting in better color quality and smaller file size.
        """
        filter_chain = self._build_filter_chain()
        palette_path = os.path.join(tempfile.gettempdir(), f"gifmemore_palette_{os.getpid()}.png")
        
        # Pass 1: Generate palette
        palette_cmd = [
            "ffmpeg",
            "-ss", str(self.config.start),
            "-t", str(self.config.duration),
            "-i", self.config.input_file,
            "-vf", f"{filter_chain},palettegen=stats_mode={self.config.stats_mode}",
            "-y",
            palette_path
        ]
        
        self._run_command(palette_cmd, "Palette generation")
        
        # Verify palette was created
        if not os.path.exists(palette_path):
            raise FileNotFoundError("Palette generation failed - palette file not created")
        
        # Pass 2: Create GIF using palette
        gif_cmd = [
            "ffmpeg",
            "-ss", str(self.config.start),
            "-t", str(self.config.duration),
            "-i", self.config.input_file,
            "-i", palette_path,
            "-lavfi", f"{filter_chain}[x];[x][1:v]paletteuse",
            "-y",
            "-loop", str(self.config.loop),
            self.output_path
        ]
        
        try:
            self._run_command(gif_cmd, "GIF creation")
        finally:
            # Cleanup palette (even if GIF creation fails)
            if os.path.exists(palette_path):
                os.remove(palette_path)
        
        print(f"✓ High-quality GIF created at {self.output_path}")
        if self.config.clipboard:
            copy_gif_to_clipboard(self.output_path)
        if self.config.open_gif:
            self._open_gif()

    def preview(self):
        """Preview the video segment with filters using ffplay"""
        filter_chain = self._build_filter_chain()
        
        cmd = [
            "ffplay",
            "-ss", str(self.config.start),
            "-t", str(self.config.duration),
            "-i", self.config.input_file,
            "-vf", filter_chain,
            "-loop", "0",
            "-autoexit"
        ]
        
        print("\nOpening preview... (Close the window to continue)")
        print(" ".join(cmd))
        print()
        
        try:
            subprocess.run(cmd, check=False)
        except FileNotFoundError:
            print("Warning: ffplay not found. Install FFmpeg to use preview.")
            print("Skipping preview...")
        except Exception as e:
            print(f"Preview failed: {e}")
            print("Continuing with GIF creation...")
    
    def create(self):
        """Create GIF using configured method"""
        if self.config.preview:
            self.preview()
            response = input("\nContinue with GIF creation? [Y/n]: ").strip().lower()
            if response in ['n', 'no']:
                print("✗ GIF creation cancelled.")
                return
            print()
        
        if self.config.method == 'two-pass':
            self.create_two_pass()
        else:
            self.create_single_pass()
