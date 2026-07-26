import re
import subprocess


def _available_capture_devices():
    """Return sorted ALSA capture card indices from arecord -l."""
    try:
        result = subprocess.run(
            ["arecord", "-l"],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:
        return []

    if result.returncode != 0:
        return []

    indices = set()
    for line in result.stdout.splitlines():
        match = re.search(r"card\s+(\d+):", line)
        if match:
            indices.add(int(match.group(1)))
    return sorted(indices)


def _capture_device_details():
    """Return capture devices as dicts with card index and description."""
    try:
        result = subprocess.run(
            ["arecord", "-l"],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:
        return []

    if result.returncode != 0:
        return []

    devices = []
    for line in result.stdout.splitlines():
        match = re.search(r"card\s+(\d+):\s*([^,]+),\s*device\s+(\d+):\s*(.+)$", line)
        if not match:
            continue
        card = int(match.group(1))
        card_name = match.group(2).strip()
        device = int(match.group(3))
        device_name = match.group(4).strip()
        description = f"{card_name} {device_name}".strip()
        devices.append(
            {
                "card": card,
                "device": device,
                "description": description,
                "line": line.strip(),
            }
        )
    return devices


def resolve_capture_device(preferred, preferred_name="", preferred_name_match_index=0):
    """
    Pick a safe capture device index.
    Falls back to the first available card, then 0 if none are discoverable.
    """
    try:
        preferred_index = int(str(preferred))
    except (TypeError, ValueError):
        preferred_index = 0

    try:
        match_index = int(preferred_name_match_index)
    except (TypeError, ValueError):
        match_index = 0
    if match_index < 0:
        match_index = 0

    devices = _capture_device_details()
    available_cards = [dev["card"] for dev in devices]
    if preferred_name:
        needle = preferred_name.lower().strip()
        matches = []
        for dev in devices:
            if needle in dev["description"].lower() or needle in dev["line"].lower():
                matches.append(dev)
        if matches:
            selected = matches[min(match_index, len(matches) - 1)]
            selected_card = selected["card"]
            try:
                return str(available_cards.index(selected_card))
            except ValueError:
                return "0"

    if not available_cards:
        return str(preferred_index if preferred_index >= 0 else 0)

    # Preferred index is interpreted as whisper-stream capture index first.
    if 0 <= preferred_index < len(available_cards):
        return str(preferred_index)

    # If a literal ALSA card ID was provided, map it to whisper-stream index.
    if preferred_index in available_cards:
        return str(available_cards.index(preferred_index))

    return "0"