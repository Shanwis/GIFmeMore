"""GIFMeMore - Create high-quality GIFs from video files"""

from .config import GIFConfig
from .filters import FilterBuilder
from .creator import GIFCreator

__version__ = "2.0.0"
__all__ = ["GIFConfig", "FilterBuilder", "GIFCreator"]
