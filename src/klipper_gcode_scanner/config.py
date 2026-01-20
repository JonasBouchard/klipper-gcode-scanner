from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    tomllib = None


@dataclass
class Settings:
    mount_base: Path = Path("/media/usb")
    gcode_dir: Path = Path("/home/pi/printer_data/gcodes")
    extensions: tuple[str, ...] = (".gcode",)
    scan_interval: float = 5.0
    state_path: Path = Path("/var/lib/klipper-gcode-scanner/state.json")
    log_level: str = "INFO"

    @classmethod
    def from_file(cls, path: Path) -> "Settings":
        if not path.exists():
            return cls()
        if tomllib is None:
            raise RuntimeError("TOML configuration requires Python 3.11+")
        data = tomllib.loads(path.read_text())
        return cls(
            mount_base=Path(data.get("mount_base", cls.mount_base)),
            gcode_dir=Path(data.get("gcode_dir", cls.gcode_dir)),
            extensions=tuple(data.get("extensions", cls.extensions)),
            scan_interval=float(data.get("scan_interval", cls.scan_interval)),
            state_path=Path(data.get("state_path", cls.state_path)),
            log_level=str(data.get("log_level", cls.log_level)).upper(),
        )


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_state(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_state(path: Path, state: dict[str, list[str]]) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(state, indent=2, sort_keys=True))


def normalize_extensions(extensions: Iterable[str]) -> tuple[str, ...]:
    normalized = []
    for ext in extensions:
        ext = ext.lower().strip()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        normalized.append(ext)
    return tuple(dict.fromkeys(normalized))
