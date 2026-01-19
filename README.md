# klipper-gcode-scanner

## Description
**klipper-gcode-scanner** is a Klipper ecosystem extension that automatically detects removable storage devices (such as USB flash drives) connected to the printer host and scans their root directory for G-code files. Any `.gcode` files found are made available in KlipperScreen alongside G-code files already stored locally on the printer.

The scan is intentionally limited to the filesystem root to ensure fast, predictable behavior and avoid unnecessary directory traversal.

## Goals
- Eliminate the need to manually copy G-code files onto the printer host.
- Provide a seamless, plug-and-print workflow using removable media.
- Integrate cleanly with Klipper, Moonraker, and KlipperScreen.

## Expected Behavior
1. A removable storage device is connected to the printer host (e.g. Raspberry Pi).
2. The system detects the device and mounts it (if not already mounted).
3. The root of the mounted filesystem is scanned (non-recursive).
4. All `.gcode` files found are exposed to KlipperScreen together with local G-code files.
5. When the device is removed, the associated G-code entries are removed automatically.

## Surface Scan Definition
- Only files located directly in the mount point root are considered.
- No recursion into subdirectories.
- Files are filtered by extension: `.gcode`.

## Functional Requirements
- Automatic detection of insertion and removal of removable storage devices.
- Support for multiple removable devices connected simultaneously.
- Live updates to the G-code list in KlipperScreen.
- Prevention of duplicate entries when devices are reconnected.
- Safe handling of filename collisions (prefixing or virtual folders).

## Non-Functional Requirements
- Fast and lightweight scanning to avoid UI lag.
- Read-only interaction with removable media.
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
- `enabled: true | false`
- `mount_base: /media/usb`
- `scan_depth: 0`
- `extensions: [".gcode"]`
- `presentation_mode: prefix | virtual_folder`
- `auto_mount: true | false`
- `read_only: true`

## User Experience
- Plug in a USB drive → G-code files at the root appear automatically in KlipperScreen.
- Remove the drive → those files disappear.
- No manual file management on the printer host is required.

## Out of Scope
- Recursive directory scanning.
- Automatic copying of files to local storage.
- Advanced G-code analysis (previews, thumbnails, time estimation).
- Support for non-G-code file types.

## Notes
This project focuses on simplicity, reliability, and tight integration with the Klipper ecosystem by providing a fast, surface-level G-code discovery mechanism for removable storage devices.
