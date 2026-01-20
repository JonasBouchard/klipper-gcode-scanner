from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path

from .config import Settings, load_state, normalize_extensions, save_state

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    devices: dict[str, Path]
    files_by_device: dict[str, list[Path]]


class GcodeScanner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.extensions = normalize_extensions(settings.extensions)
        self.usb_root = settings.gcode_dir / "usb"
        self.state: dict[str, list[str]] = load_state(settings.state_path)

    def discover_devices(self) -> dict[str, Path]:
        devices: dict[str, Path] = {}
        if not self.settings.mount_base.exists():
            return devices
        for entry in self.settings.mount_base.iterdir():
            if not entry.is_dir():
                continue
            if os.path.ismount(entry):
                devices[entry.name] = entry
        return devices

    def scan_device(self, device_path: Path) -> list[Path]:
        files = []
        for entry in device_path.iterdir():
            if entry.is_file() and entry.suffix.lower() in self.extensions:
                files.append(entry)
        return files

    def scan(self) -> ScanResult:
        devices = self.discover_devices()
        files_by_device: dict[str, list[Path]] = {}
        for label, path in devices.items():
            files_by_device[label] = self.scan_device(path)
        return ScanResult(devices=devices, files_by_device=files_by_device)

    def apply(self, result: ScanResult) -> None:
        self.usb_root.mkdir(parents=True, exist_ok=True)
        updated_state: dict[str, list[str]] = {}

        for label, files in result.files_by_device.items():
            device_dir = self.usb_root / label
            device_dir.mkdir(parents=True, exist_ok=True)
            current_links: list[str] = []

            for file_path in files:
                link_path = device_dir / file_path.name
                current_links.append(str(link_path))
                if link_path.exists():
                    if link_path.is_symlink() and link_path.resolve() == file_path:
                        continue
                    link_path.unlink()
                link_path.symlink_to(file_path)
                logger.info("Linked %s -> %s", link_path, file_path)

            for existing in list(device_dir.iterdir()):
                if str(existing) not in current_links:
                    if existing.is_symlink() or existing.is_file():
                        existing.unlink()
                        logger.info("Removed stale link %s", existing)

            updated_state[label] = current_links

        for label in set(self.state) - set(result.files_by_device):
            device_dir = self.usb_root / label
            if device_dir.exists():
                for entry in device_dir.iterdir():
                    if entry.is_symlink() or entry.is_file():
                        entry.unlink()
                        logger.info("Removed link %s", entry)
                try:
                    device_dir.rmdir()
                except OSError:
                    logger.warning("Unable to remove directory %s", device_dir)

        self.state = updated_state
        save_state(self.settings.state_path, self.state)

    def run_once(self) -> None:
        result = self.scan()
        self.apply(result)

    def run_forever(self) -> None:
        logger.info("Starting klipper-gcode-scanner with interval %.1fs", self.settings.scan_interval)
        while True:
            try:
                self.run_once()
            except Exception:
                logger.exception("Scan failed")
            time.sleep(self.settings.scan_interval)
