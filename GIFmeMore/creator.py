"""GIF creation engine"""

import os
import subprocess
from datetime import datetime
from typing import List

from .config import GIFConfig
from .filters import FilterBuilder


class GIFCreator:
    """Creates GIFs from video files using FFmpeg"""
    
    def __init__(self, config: GIFConfig):
        self.config = config
        self._validate_input()
        self._prepare_output()
    
    def _validate_input(self):
        """Validate input file exists"""
        if not os.path.exists(self.config.input_file):
            raise FileNotFoundError(f"Input file not found: {self.config.input_file}")
    
    def _prepare_output(self):
        """Prepare output directory and filename"""
        os.makedirs("output", exist_ok=True)
        
        if self.config.output_file == "output.gif":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.config.output_file = f"output_{timestamp}.gif"
        
        self.output_path = os.path.join("output", self.config.output_file)
    
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
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"{description} failed: {e.stderr.decode()}")
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
            self.output_path
        ]
        
        self._run_command(cmd, "Single-pass")
        print(f"✓ GIF created at {self.output_path}")
    
    def create_two_pass(self):
        """Create GIF using two-pass method (slower, higher quality)
        
        This method generates a custom palette first, then uses it to create
        the GIF, resulting in better color quality and smaller file size.
        """
        filter_chain = self._build_filter_chain()
        palette_path = "output/palette.png"
        
        # Pass 1: Generate palette
        palette_cmd = [
            "ffmpeg",
            "-ss", str(self.config.start),
            "-t", str(self.config.duration),
            "-i", self.config.input_file,
            "-vf", f"{filter_chain},palettegen",
            "-y",
            palette_path
        ]
        
        self._run_command(palette_cmd, "Palette generation")
        
        # Pass 2: Create GIF using palette
        gif_cmd = [
            "ffmpeg",
            "-ss", str(self.config.start),
            "-t", str(self.config.duration),
            "-i", self.config.input_file,
            "-i", palette_path,
            "-lavfi", f"{filter_chain}[x];[x][1:v]paletteuse",
            "-y",
            self.output_path
        ]
        
        self._run_command(gif_cmd, "GIF creation")
        
        # Cleanup palette
        if os.path.exists(palette_path):
            os.remove(palette_path)
        
        print(f"✓ High-quality GIF created at {self.output_path}")
    
    def create(self):
        """Create GIF using configured method"""
        if self.config.method == 'two-pass':
            self.create_two_pass()
        else:
            self.create_single_pass()
