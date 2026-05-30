"""Cross-platform clipboard copy for GIF files"""

import os
import platform
import shutil
import subprocess


def copy_gif_to_clipboard(filepath: str) -> None:
    system = platform.system()

    if system == "Darwin":
        _copy_macos(filepath)
    elif system == "Windows":
        _copy_windows(filepath)
    elif system == "Linux":
        _copy_linux(filepath)
    else:
        print(f"Clipboard copy not supported on {system}")


def _copy_macos(filepath: str) -> None:
    abs_path = os.path.abspath(filepath)
    script = (
        'ObjC.import("AppKit");'
        f'var url = $.NSURL.fileURLWithPath("{abs_path}");'
        'var pb = $.NSPasteboard.generalPasteboard;'
        'pb.clearContents();'
        'pb.writeObjects([url]);'
    )
    try:
        subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", script],
            check=True, timeout=5
        )
        print("\u2713 GIF copied to clipboard")
    except subprocess.TimeoutExpired:
        print("Clipboard copy timed out — osascript did not respond")
    except subprocess.CalledProcessError as e:
        print(f"Clipboard copy failed: {e.stderr.decode() if e.stderr else e}")


def _copy_windows(filepath: str) -> None:
    abs_path = os.path.abspath(filepath)
    ps_cmd = (
        f'Add-Type -AssemblyName System.Windows.Forms; '
        f'$paths = New-Object Collections.Specialized.StringCollection; '
        f'$paths.Add("{abs_path}"); '
        f'[Windows.Forms.Clipboard]::SetFileDropList($paths)'
    )
    try:
        subprocess.run(
            ["powershell", "-Command", ps_cmd],
            check=True, timeout=5
        )
        print("\u2713 GIF copied to clipboard")
    except subprocess.TimeoutExpired:
        print("Clipboard copy timed out — PowerShell did not respond")
    except subprocess.CalledProcessError as e:
        print(f"Clipboard copy failed: {e.stderr.decode() if e.stderr else e}")


def _is_wayland() -> bool:
    return "WAYLAND_DISPLAY" in os.environ or os.environ.get("XDG_SESSION_TYPE") == "wayland"


def _try_run(args, input_data, tool_name, timeout=5):
    try:
        subprocess.run(
            args, input=input_data, check=True, timeout=timeout
        )
        return True
    except subprocess.TimeoutExpired:
        print(f"{tool_name} timed out — check your display server")
    except subprocess.CalledProcessError as e:
        msg = e.stderr.decode() if e.stderr else str(e)
        print(f"{tool_name} failed: {msg}")
    return False


def _copy_linux(filepath: str) -> None:
    abs_path = os.path.abspath(filepath)
    uri = f"file://{abs_path}\r\n"
    wayland = _is_wayland()

    if wayland:
        primary = ("wl-copy", ["wl-copy", "-t", "text/uri-list"])
        fallback = ("xclip", ["xclip", "-selection", "clipboard", "-target", "text/uri-list"])
        note = (
            "wl-clipboard not found — using xclip through XWayland (may be slow).\n"
            "  Install: sudo dnf install wl-clipboard"
        )
    else:
        primary = ("xclip", ["xclip", "-selection", "clipboard", "-target", "text/uri-list"])
        fallback = ("wl-copy", ["wl-copy", "-t", "text/uri-list"])
        note = (
            "xclip not found — using wl-copy through XWayland (may be slow).\n"
            "  Install: sudo dnf install xclip"
        )

    for is_fallback, (name, args) in [(False, primary), (True, fallback)]:
        if not shutil.which(name):
            continue
        if is_fallback:
            print(f"Note: {note}")
        if _try_run(args, uri.encode(), name):
            print(f"\u2713 GIF copied to clipboard (via {name})")
            return

    pkg = "wl-clipboard" if wayland else "xclip"
    display = "Wayland" if wayland else "X11"
    print(
        f"Clipboard copy needs wl-clipboard or xclip.\n"
        f"  Install: sudo dnf install {pkg}    # {display} (recommended)\n"
        f"  Install: sudo apt install {pkg}    # Debian/Ubuntu\n"
        f"  Install: sudo pacman -S {pkg}      # Arch"
    )
