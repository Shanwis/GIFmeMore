"""Configuration and preset management"""

import json
import os
import sys


def get_default_config_dir() -> str:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "gifmemore")
    elif sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library",
                            "Application Support", "gifmemore")
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME",
                             os.path.join(os.path.expanduser("~"), ".config"))
        return os.path.join(xdg, "gifmemore")


def get_default_config_path() -> str:
    return os.path.join(get_default_config_dir(), "config.json")


def create_default_config(path: str) -> dict:
    data = {
        "start": 0,
        "duration": 5,
        "fps": 15,
        "speedup": 1.0,
        "resize": 1.0,
        "text": "",
        "position": "center",
        "fontsize": 50,
        "color": "white",
        "loop": 0,
        "method": "two-pass",
        "preview": False,
        "presets": {}
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return data


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def resolve_config(data: dict, preset_name: str = None) -> dict:
    presets = data.get("presets", {})
    merged = {k: v for k, v in data.items() if k != "presets"}
    if preset_name:
        if preset_name not in presets:
            available = ", ".join(f'"{p}"' for p in sorted(presets.keys()))
            parts = [f'Error: Preset "{preset_name}" not found.']
            if available:
                parts.append(f"Available presets: {available}")
            parts.append(f"Edit config file at: {get_default_config_path()}")
            raise KeyError("\n".join(parts))
        merged.update(presets[preset_name])
    return merged
