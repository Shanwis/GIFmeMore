"""URL detection and download using yt-dlp"""

import os
import re
import shutil
import subprocess
import tempfile

from .logger import log

URL_PATTERN = re.compile(r'^https?://', re.IGNORECASE)

YTDLP_DOWNLOAD_MSG = """
URL detected: {url}
gifmemore can download videos from URLs using yt-dlp.

Install yt-dlp:
  pip install yt-dlp

Then run again for automatic download:
  gifmemore -f "{url}" [options]

Or download manually:
  yt-dlp "{url}" -o video.mp4
  gifmemore -f video.mp4 [options]
"""


def is_url(value: str) -> bool:
    return bool(URL_PATTERN.match(value.strip()))


def is_ytdlp_available() -> bool:
    return shutil.which("yt-dlp") is not None


def print_download_instructions(url: str):
    print(YTDLP_DOWNLOAD_MSG.format(url=url))


class VideoDownloader:
    def __init__(self, url: str):
        self.url = url
        self._tmpdir = None
        self.downloaded_file = None

    def download(self) -> str:
        self._tmpdir = tempfile.mkdtemp(prefix="gifmemore_")
        output_template = os.path.join(self._tmpdir, "%(title)s.%(ext)s")

        cmd = [
            "yt-dlp",
            "-f", "bv*+ba/b",
            "-o", output_template,
            "--merge-output-format", "mp4",
            "--no-progress",
            self.url,
        ]

        log(f"Downloading: {self.url}")
        log(f"Running: {' '.join(cmd)}")
        print(f"Downloading video...")

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)

            # Find the merged mp4 file in temp dir
            for f in os.listdir(self._tmpdir):
                if f.endswith(".mp4") and ".f" not in f:
                    self.downloaded_file = os.path.join(self._tmpdir, f)
                    break

            if not self.downloaded_file or not os.path.exists(self.downloaded_file):
                raise FileNotFoundError(
                    f"Download completed but no merged mp4 file found "
                    f"in {self._tmpdir}"
                )

            print(f"Downloaded: {os.path.basename(self.downloaded_file)}")
            return self.downloaded_file

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Download failed:\n{e.stderr}")

    def cleanup(self):
        if self._tmpdir and os.path.exists(self._tmpdir):
            shutil.rmtree(self._tmpdir, ignore_errors=True)
