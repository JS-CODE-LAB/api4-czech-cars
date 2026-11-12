"""Binary sensors: every YES/NO or true/false field returned by the API."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .groups import functional_group, binary_device_class
from .localization import localized_path
from .coordinator import SkodaConfigEntry, SkodaCoordinator
from .entity import KIND_BINARY, SkodaEntity, classify, humanize, to_bool


CHARGING_STATE_PATH = "charging.status.state"


async def async_setup_entry(
    hass: HomeAssistant, entry: SkodaConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    known: set[str] = set()
    charging_added = False

    @callback
    def _discover() -> None:
        nonlocal charging_added
        if coordinator.data is None:
            return
        if not charging_added and CHARGING_STATE_PATH in coordinator.data.flat:
            charging_added = True
            async_add_entities([SkodaBatteryChargingSensor(coordinator)])
        new = [
            SkodaFieldBinarySensor(coordinator, path)
            for path, value in coordinator.data.flat.items()
            if path not in known and classify(value) == KIND_BINARY
        ]
        known.update(e.field_path for e in new)
        if new:
            async_add_entities(new)

    _discover()
    entry.async_on_unload(coordinator.async_add_listener(_discover))


class SkodaFieldBinarySensor(SkodaEntity, BinarySensorEntity):
    def __init__(self, coordinator: SkodaCoordinator, path: str) -> None:
        super().__init__(coordinator)
        self.field_path = path
        self._attr_unique_id = f"{self._vin}_{path}"
        self._attr_translation_key = "api_field"
        self._attr_translation_placeholders = {
            "field": localized_path(path, coordinator.hass.config.language)
        }
        self._group = functional_group(path)
        self._device_group = self._group
        device_class = binary_device_class(path)
        if device_class:
            self._attr_device_class = BinarySensorDeviceClass(device_class)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {"functional_group": self._group, "api_path": self.field_path}

    @property
    def is_on(self) -> bool | None:
        value: Any = self.coordinator.data.flat.get(self.field_path)
        return to_bool(value)


class SkodaBatteryChargingSensor(SkodaEntity, BinarySensorEntity):
    """On while charging; HA shows the charging icon next to the battery level."""

    _attr_translation_key = "battery_charging"
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    def __init__(self, coordinator: SkodaCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_battery_charging"
        self._device_group = "charging"

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.flat.get(CHARGING_STATE_PATH)
        return value.upper() == "CHARGING" if isinstance(value, str) else None
