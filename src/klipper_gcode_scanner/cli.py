from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .config import Settings
from .scanner import GcodeScanner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan removable media for G-code files.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("/etc/klipper-gcode-scanner/config.toml"),
        help="Path to TOML configuration file.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("scan", help="Run a single scan.")
    subparsers.add_parser("daemon", help="Run continuously.")
    return parser


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    settings = Settings.from_file(args.config)
    configure_logging(settings.log_level)

    scanner = GcodeScanner(settings)

    if args.command == "scan":
        scanner.run_once()
    else:
        scanner.run_forever()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
