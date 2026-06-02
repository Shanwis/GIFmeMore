"""Configuration for GIF creation"""

from dataclasses import dataclass


@dataclass
class GIFConfig:
    """Configuration for GIF creation"""
    input_file: str
    output_file: str
    start: int = 0
    duration: int = 5
    fps: int = 15
    speedup: float = 1.0
    resize: float = 1.0
    text: str = ''
    position: str = 'center'
    fontsize: int = 50
    color: str = 'white'
    loop: int = 0
    method: str = 'two-pass'  # 'single-pass' or 'two-pass'
    preview: bool = False  # Preview before creating GIF
    clipboard: bool = False  # copy result to clipboard
    open_gif: bool = False  # Open GIF after creation
    stats_mode: str = 'diff'  # Palette statistics mode: 'full', 'diff', or 'single'
    rotation: int = 0  # Video rotation in degrees (0/90/180/270)
    width: int = 0  # Original video width (from ffprobe)
    height: int = 0  # Original video height (from ffprobe)
