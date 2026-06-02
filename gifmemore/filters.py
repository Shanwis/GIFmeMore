"""FFmpeg filter chain builder"""

from typing import List
from .config import GIFConfig


class FilterBuilder:
    """Builds FFmpeg filter chains using the builder pattern"""
    
    POSITION_MAP = {
        "top_left": "10:10",
        "top_right": "W-tw-10:10",
        "bottom_left": "10:H-th-10",
        "bottom_right": "W-tw-10:H-th-10",
        "center": "(W-tw)/2:(H-th)/2",
        "top": "(W-tw)/2:10",
        "bottom": "(W-tw)/2:H-th-10"
    }
    
    def __init__(self, config: GIFConfig):
        self.config = config
        self.filters: List[str] = []
    
    def add_rotation_filter(self) -> 'FilterBuilder':
        """Fix video orientation based on rotation metadata"""
        if self.config.rotation == 90:
            self.filters.append("transpose=1")
        elif self.config.rotation == 270:
            self.filters.append("transpose=2")
        elif self.config.rotation == 180:
            self.filters.append("transpose=3")
        return self
    
    def add_speed_filter(self) -> 'FilterBuilder':
        """Add speed adjustment filter"""
        if self.config.speedup != 1.0:
            self.filters.append(f"setpts={1/self.config.speedup}*PTS")
        return self
    
    def add_resize_filter(self) -> 'FilterBuilder':
        """Add resize filter"""
        if self.config.resize != 1.0:
            self.filters.append(f"scale=iw*{self.config.resize}:ih*{self.config.resize}")
        return self
    
    def add_fps_filter(self) -> 'FilterBuilder':
        """Add FPS filter"""
        self.filters.append(f"fps={self.config.fps}")
        return self
    
    def _word_wrap(self, text: str, max_chars: int) -> List[str]:
        """Split text at word boundaries so no line exceeds max_chars"""
        words = text.split()
        lines, current = [], []
        for word in words:
            char_count = sum(len(w) for w in current) + len(current) + len(word)
            if not current or char_count <= max_chars:
                current.append(word)
            else:
                lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
        return lines

    def _prepare_text(self, text: str, max_chars: int) -> str:
        """Word-wrap and escape text for FFmpeg drawtext"""
        lines = self._word_wrap(text, max_chars)
        return "\n".join(
            line.replace("\\", "\\\\").replace("'", "\\'")
            for line in lines
        )
    
    def add_text_filter(self) -> 'FilterBuilder':
        """Add text overlay filter"""
        if self.config.text:
            display_w = self.config.width
            if self.config.rotation in (90, 270):
                display_w = self.config.height
            effective_w = int(display_w * self.config.resize)
            avg_char_w = self.config.fontsize * 0.6
            if avg_char_w > 0 and effective_w > 0:
                max_chars = max(1, int(effective_w / avg_char_w) - 2)
            else:
                max_chars = 999

            escaped = self._prepare_text(self.config.text, max_chars)
            pos = self.POSITION_MAP.get(self.config.position, "(W-tw)/2:(H-th)/2")
            drawtext = (
                f"drawtext=text='{escaped}':"
                f"fontcolor={self.config.color}:"
                f"fontsize={self.config.fontsize}:"
                f"x={pos.split(':')[0]}:y={pos.split(':')[1]}"
            )
            self.filters.append(drawtext)
        return self
    
    def build(self) -> str:
        """Build the complete filter chain"""
        return ",".join(self.filters)
