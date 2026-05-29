"""gifmemore - Create high-quality GIFs from video files using FFmpeg"""

from .config import GIFConfig
from .filters import FilterBuilder
from .creator import GIFCreator

__version__ = "1.1.1"
__all__ = ["GIFConfig", "FilterBuilder", "GIFCreator"]
