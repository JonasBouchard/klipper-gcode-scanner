# klipper-gcode-scanner 🔍

## Description
**klipper-gcode-scanner** is a Klipper ecosystem extension that automatically detects removable storage devices (such as USB flash drives) connected to the printer host and scans their root directory for G-code files. Any `.gcode` files found are made available in KlipperScreen alongside G-code files already stored locally on the printer.

The scan is intentionally limited to the filesystem root to ensure fast, predictable behavior and avoid unnecessary directory traversal.

## Goals
- Eliminate the need to manually copy G-code files onto the printer host.
- Provide a seamless, plug-and-print workflow using removable media.

## Behavior
1. A removable storage device is connected to the printer host.
2. The system detects the device and mounts it (if not already mounted).
3. The root of the mounted filesystem is scanned.
4. All `.gcode` files found are exposed to KlipperScreen together with local G-code files.
5. When the device is removed, the associated G-code entries are removed automatically.

## Functional Requirements
- Automatic detection of insertion and removal of removable storage devices.
- Support for multiple removable devices connected simultaneously.
- Live updates to the G-code list in KlipperScreen.
- Prevention of duplicate entries when devices are reconnected.
- Safe handling of filename collisions.

## Non-Functional Requirements
- Fast and lightweight scanning to avoid UI lag.
- Graceful handling of slow, unsupported, or faulty devices.
- Clear logging for debugging and maintenance.

## Target Integration
- **Device detection**: via `udev`, `systemd`, or equivalent Linux mechanisms.
- **Backend**: implemented as a Moonraker plugin or companion service that:
  - indexes G-code files found on removable media
  - exposes them to KlipperScreen through Moonraker’s file interface or API
- **Frontend**: KlipperScreen displays USB-derived G-codes together with local files without special user interaction.

## Proposed Workflow
1. `udev` detects a storage device `add` event.
2. The device is mounted under a known base directory (e.g. `/media/usb/<label>`).
3. The mount root is scanned for `.gcode` files.
4. Discovered files are made available to Moonraker:
   - via symlinks in a monitored G-code directory, or
   - via a dedicated Moonraker API endpoint.
5. KlipperScreen refreshes and displays the updated file list.
6. On device removal, related entries are cleaned up and removed from the UI.

## Edge Cases
- Devices already connected at system startup.
- Multiple devices with identical filenames.
- Device removal during scanning.
- Filesystem permission or ownership issues.
- Different filesystem formats (FAT32, exFAT, NTFS).

## Configuration Ideas
- `advanced configuration: true | false`
- `mount_base: /media/usb`
- `scan_depth: 0`
- `extensions: [".gcode"]`
- `auto_mount: true | false`

## User Experience
- Plug in a USB drive → G-code files at the root appear automatically in KlipperScreen.
- Remove the drive → those files disappear.
- No manual file management on the printer host is required.

## Notes
This project focuses on simplicity, reliability, and tight integration with the Klipper ecosystem by providing a fast, surface-level G-code discovery mechanism for removable storage devices.

## Installation
### Requirements
- Python 3.9+
- A Klipper/Moonraker host with a writable G-code directory (e.g. `~/printer_data/gcodes`)
- Removable media mounted under a predictable base path (default: `/media/usb`)

### Quick install (recommended)
1. Install the package:
   ```bash
   pip install .
   ```
2. Install the configuration file:
   ```bash
   sudo mkdir -p /etc/klipper-gcode-scanner
   sudo cp config/klipper-gcode-scanner.toml /etc/klipper-gcode-scanner/config.toml
   ```
3. Install the systemd service:
   ```bash
   sudo cp systemd/klipper-gcode-scanner.service /etc/systemd/system/klipper-gcode-scanner.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now klipper-gcode-scanner.service
   ```

### Manual usage
Run a single scan:
```bash
klipper-gcode-scanner --config /etc/klipper-gcode-scanner/config.toml scan
```

Run continuously (foreground):
```bash
klipper-gcode-scanner --config /etc/klipper-gcode-scanner/config.toml daemon
```

### Configuration
The default configuration file is provided at `config/klipper-gcode-scanner.toml`. Adjust paths as needed:
- `mount_base`: where removable drives are mounted.
- `gcode_dir`: Moonraker G-code directory that KlipperScreen monitors.
- `extensions`: list of file extensions to expose.
- `scan_interval`: scan interval in seconds.
- `state_path`: where the scanner records the device state.
