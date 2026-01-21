#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="/etc/klipper-gcode-scanner"
SERVICE_PATH="/etc/systemd/system/klipper-gcode-scanner.service"
RUN_USER="${SUDO_USER:-$USER}"
RUN_GROUP="${SUDO_USER:-$USER}"
MOONRAKER_CONFIG="/home/${RUN_USER}/printer_data/config/moonraker.conf"
UPDATE_MANAGER_TEMPLATE="${REPO_DIR}/moonraker_update.txt"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run with sudo: sudo ./install.sh"
  exit 1
fi

install -d -m 755 "${CONFIG_DIR}"
install -m 644 "${REPO_DIR}/config/klipper-gcode-scanner.toml" "${CONFIG_DIR}/config.toml"

sed \
  -e "s|@REPO_DIR@|${REPO_DIR}|g" \
  -e "s|@USER@|${RUN_USER}|g" \
  -e "s|@GROUP@|${RUN_GROUP}|g" \
  "${REPO_DIR}/systemd/klipper-gcode-scanner.service" \
  > "${SERVICE_PATH}"

systemctl daemon-reload
systemctl enable --now klipper-gcode-scanner.service

UPDATE_MANAGER_BLOCK="$(sed "s|@REPO_DIR@|${REPO_DIR}|g" "${UPDATE_MANAGER_TEMPLATE}")"

if [[ -f "${MOONRAKER_CONFIG}" ]]; then
  if ! grep -q "^[[]update_manager klipper-gcode-scanner[]]$" "${MOONRAKER_CONFIG}"; then
    printf "\n%s\n" "${UPDATE_MANAGER_BLOCK}" >> "${MOONRAKER_CONFIG}"
    echo "Added update_manager block to ${MOONRAKER_CONFIG}."
  else
    echo "update_manager block already present in ${MOONRAKER_CONFIG}."
  fi
else
  echo "Moonraker config not found at ${MOONRAKER_CONFIG}."
  echo "Add the following block manually when ready:"
  echo "${UPDATE_MANAGER_BLOCK}"
fi

echo "Installed klipper-gcode-scanner service for user ${RUN_USER}."
