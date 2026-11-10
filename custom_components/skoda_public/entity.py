"""Shared entity helpers."""
from __future__ import annotations

import re
import time
from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SkodaCoordinator

BOOL_TRUE = {"YES", "TRUE", "ON"}
BOOL_FALSE = {"NO", "FALSE", "OFF"}

KIND_BINARY = "binary"
KIND_SENSOR = "sensor"


def classify(value: Any) -> str:
    """Decide which platform a scalar belongs to."""
    if isinstance(value, bool):
        return KIND_BINARY
    if isinstance(value, str) and value.upper() in BOOL_TRUE | BOOL_FALSE:
        return KIND_BINARY
    return KIND_SENSOR


def to_bool(value: Any) -> bool | None:
    """Convert API boolean-ish values; unknown stays None."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        upper = value.upper()
        if upper in BOOL_TRUE:
            return True
        if upper in BOOL_FALSE:
            return False
    return None


def humanize(path: str) -> str:
    """'charging.status.stateOfChargeInPercent' -> 'Charging status state of charge in percent'."""
    parts: list[str] = []
    for seg in path.split("."):
        if seg.isdigit():
            parts.append(str(int(seg) + 1))
        else:
            parts.append(re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", seg).lower())
    text = " ".join(parts)
    return text[:1].upper() + text[1:]


def find_positions(flat: dict[str, Any]) -> dict[str, tuple[str, str]]:
    """Find latitude/longitude pairs sharing a prefix -> {prefix: (lat_path, lon_path)}."""
    lowered = {p.lower(): p for p in flat}
    found: dict[str, tuple[str, str]] = {}
    for path, value in flat.items():
        prefix, _, last = path.rpartition(".")
        if last.lower() not in ("latitude", "lat") or isinstance(value, bool):
            continue
        if not isinstance(value, (int, float)):
            continue
        for cand in ("longitude", "lon", "lng"):
            lon_key = f"{prefix}.{cand}" if prefix else cand
            lon_path = lowered.get(lon_key.lower())
            if lon_path and isinstance(flat[lon_path], (int, float)):
                found[prefix] = (path, lon_path)
                break
    return found


SOC_EXACT = "charging.status.battery.stateOfChargeInPercent"
_SOC_NAMES = {
    "stateofchargeinpercent",
    "currentsocinpercent",
    "currentstateofchargeinpercent",
    "socinpercent",
}
_SOC_EXCLUDE = ("target", "limit", "settings", "profile")


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def find_soc_path(flat: dict[str, Any]) -> str | None:
    """Locate the *current* battery state of charge (not the charging target)."""
    if _is_number(flat.get(SOC_EXACT)):
        return SOC_EXACT
    candidates = []
    for path, value in flat.items():
        if not _is_number(value):
            continue
        low = path.lower()
        if low.rsplit(".", 1)[-1] in _SOC_NAMES and not any(x in low for x in _SOC_EXCLUDE):
            candidates.append(path)
    candidates.sort(key=lambda p: ("charging" not in p.lower(), len(p)))
    return candidates[0] if candidates else None


def find_range_path(flat: dict[str, Any]) -> str | None:
    """Locate the current remaining range (prefers the electric one)."""
    candidates = []
    for path, value in flat.items():
        if not _is_number(value):
            continue
        low = path.lower()
        last = low.rsplit(".", 1)[-1]
        if "range" in last and last.endswith(("inmeters", "inkm")):
            candidates.append(path)
    candidates.sort(
        key=lambda p: (
            not any(k in p.lower() for k in ("battery", "electric", "charging")),
            len(p),
        )
    )
    return candidates[0] if candidates else None


class SkodaEntity(CoordinatorEntity[SkodaCoordinator]):
    """Base entity attached to the vehicle device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SkodaCoordinator) -> None:
        super().__init__(coordinator)
        self._vin = coordinator.vin

    @property
    def device_info(self) -> DeviceInfo:
        vehicle = self.coordinator.data.vehicle if self.coordinator.data else {}
        return DeviceInfo(
            identifiers={(DOMAIN, self._vin)},
            manufacturer="Škoda Auto",
            name=vehicle.get("name") or self._vin,
            serial_number=self._vin,
        )


class SkodaControlEntity(SkodaEntity):
    """Entity that sends commands; shows the commanded state until the car reports back."""

    _optimistic: Any = None
    _optimistic_until: float = 0.0

    def _set_optimistic(self, value: Any, seconds: int = 90) -> None:
        self._optimistic = value
        self._optimistic_until = time.monotonic() + seconds
        self.async_write_ha_state()

    def _get_optimistic(self) -> Any:
        if self._optimistic is not None and time.monotonic() < self._optimistic_until:
            return self._optimistic
        self._optimistic = None
        return None
