"""Sensors: every non-boolean scalar returned by the API + diagnostics."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfEnergy,
    UnitOfLength,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .image_fields import is_image_field
from .localization import localized_path
from .groups import functional_group
from .coordinator import SkodaConfigEntry, SkodaCoordinator
from .entity import KIND_SENSOR, SkodaEntity, classify, find_range_path, find_soc_path, humanize

M = SensorStateClass.MEASUREMENT
SD = SensorDeviceClass

# (key suffix, unit, device class, state class) – matched on the lowercase last path segment.
_UNIT_TABLE = (
    ("inpercent", PERCENTAGE, None, M),
    ("inkm", UnitOfLength.KILOMETERS, SD.DISTANCE, M),
    ("inmeters", UnitOfLength.METERS, SD.DISTANCE, M),
    ("inkw", UnitOfPower.KILO_WATT, SD.POWER, M),
    ("inkwh", UnitOfEnergy.KILO_WATT_HOUR, SD.ENERGY, None),
    ("inminutes", UnitOfTime.MINUTES, SD.DURATION, None),
    ("inseconds", UnitOfTime.SECONDS, SD.DURATION, None),
    ("incelsius", UnitOfTemperature.CELSIUS, SD.TEMPERATURE, M),
    ("inliters", UnitOfVolume.LITERS, None, M),
)


def _describe(path: str, sample: Any) -> tuple[Any, Any, Any, bool]:
    """Return (unit, device_class, state_class, is_timestamp)."""
    if isinstance(sample, (int, float)) and not isinstance(sample, bool):
        low = path.lower()
        last = low.rsplit(".", 1)[-1]
        for suffix, unit, dev, state in _UNIT_TABLE:
            if last.endswith(suffix):
                if dev == SD.DISTANCE and ("odometer" in low or "mileage" in low):
                    state = SensorStateClass.TOTAL_INCREASING
                return unit, dev, state, False
        return None, None, None, False
    if isinstance(sample, str) and len(sample) >= 19 and "T" in sample:
        parsed = dt_util.parse_datetime(sample)
        if parsed is not None and parsed.tzinfo is not None:
            return None, SD.TIMESTAMP, None, True
    return None, None, None, False


async def async_setup_entry(
    hass: HomeAssistant, entry: SkodaConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        [
            SkodaRateLimitSensor(coordinator),
            SkodaKeyExpirySensor(coordinator),
            SkodaOmittedPartsSensor(coordinator),
            SkodaLastUpdateSensor(coordinator),
            SkodaLastApiErrorSensor(coordinator),
        ]
    )

    known: set[str] = set()
    battery_added = False
    range_added = False

    @callback
    def _discover() -> None:
        nonlocal battery_added, range_added
        if coordinator.data is None:
            return
        if not range_added:
            range_path = find_range_path(coordinator.data.flat)
            if range_path:
                range_added = True
                async_add_entities([SkodaRangeSensor(coordinator, range_path)])
        if not battery_added and find_soc_path(coordinator.data.flat):
            battery_added = True
            async_add_entities([SkodaBatterySensor(coordinator)])
        new = [
            SkodaFieldSensor(coordinator, path, value)
            for path, value in coordinator.data.flat.items()
            if path not in known and classify(value) == KIND_SENSOR and not is_image_field(path, value)
        ]
        known.update(e.field_path for e in new)
        if new:
            async_add_entities(new)

    _discover()
    entry.async_on_unload(coordinator.async_add_listener(_discover))


class SkodaFieldSensor(SkodaEntity, SensorEntity):
    """One API field exposed as a sensor."""

    def __init__(self, coordinator: SkodaCoordinator, path: str, sample: Any) -> None:
        super().__init__(coordinator)
        self.field_path = path
        self._attr_unique_id = f"{self._vin}_{path}"
        self._attr_translation_key = "api_field"
        self._attr_translation_placeholders = {
            "field": localized_path(path, coordinator.hass.config.language)
        }
        self._group = functional_group(path)
        self._device_group = self._group
        unit, dev, state, is_ts = _describe(path, sample)
        self._is_ts = is_ts
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = dev
        self._attr_state_class = state

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {"functional_group": self._group, "api_path": self.field_path}

    @property
    def native_value(self) -> Any:
        value = self.coordinator.data.flat.get(self.field_path)
        if value is None:
            return None
        if self._is_ts:
            return dt_util.parse_datetime(value) if isinstance(value, str) else None
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, str):
            return value[:255]
        if self._attr_device_class is None and self._attr_native_unit_of_measurement is None:
            return value
        return value


class SkodaBatterySensor(SkodaEntity, SensorEntity):
    """Current battery level. Its battery device class makes HA show it next to the device."""

    _attr_translation_key = "battery_level"
    _attr_device_class = SD.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: SkodaCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_battery_level"
        self._device_group = "battery"

    @property
    def native_value(self) -> float | None:
        flat = self.coordinator.data.flat
        path = find_soc_path(flat)
        return flat.get(path) if path else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Show which API field feeds this sensor (and any similar fields) for diagnosis."""
        flat = self.coordinator.data.flat
        similar = {
            p: v
            for p, v in flat.items()
            if any(k in p.lower() for k in ("soc", "stateofcharge", "batterylevel", "fuellevel"))
        }
        return {"source_path": find_soc_path(flat), "similar_fields": similar}


class SkodaRangeSensor(SkodaEntity, SensorEntity):
    """Current remaining range, always shown in km."""

    _attr_translation_key = "range"
    _attr_device_class = SD.DISTANCE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator: SkodaCoordinator, path: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_range"
        self._device_group = "counters"
        self._attr_native_unit_of_measurement = (
            UnitOfLength.METERS
            if path.lower().endswith("inmeters")
            else UnitOfLength.KILOMETERS
        )

    @property
    def native_value(self) -> float | None:
        flat = self.coordinator.data.flat
        path = find_range_path(flat)
        return flat.get(path) if path else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        flat = self.coordinator.data.flat
        return {
            "source_path": find_range_path(flat),
            "similar_fields": {p: v for p, v in flat.items() if "range" in p.lower()},
        }


class SkodaRateLimitSensor(SkodaEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "api_requests_remaining"
    _attr_icon = "mdi:speedometer"

    def __init__(self, coordinator: SkodaCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_api_ratelimit_remaining"
        self._device_group = "diagnostics"

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data.meta.remaining

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        meta = self.coordinator.data.meta
        return {"limit": meta.limit, "reset_in_seconds": meta.reset}


class SkodaKeyExpirySensor(SkodaEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SD.TIMESTAMP
    _attr_translation_key = "api_key_expires_at"

    def __init__(self, coordinator: SkodaCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_api_key_expires_at"
        self._device_group = "diagnostics"

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.data.meta.key_expires_at


class SkodaOmittedPartsSensor(SkodaEntity, SensorEntity):
    """Number of data parts the API reported as omitted (unsupported / unavailable)."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "omitted_data_parts"
    _attr_icon = "mdi:alert-circle-outline"

    def __init__(self, coordinator: SkodaCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_omitted_parts"
        self._device_group = "diagnostics"

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data.errors)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"errors": self.coordinator.data.errors}


class SkodaLastUpdateSensor(SkodaEntity, SensorEntity):
    """Timestamp of last successful API response."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SD.TIMESTAMP
    _attr_translation_key = "last_successful_update"

    def __init__(self, coordinator: SkodaCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_last_successful_update"
        self._device_group = "diagnostics"

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.last_successful_update


class SkodaLastApiErrorSensor(SkodaEntity, SensorEntity):
    """Last API polling error; available even if the coordinator update failed."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "last_api_error"
    _attr_icon = "mdi:alert-outline"

    def __init__(self, coordinator: SkodaCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_last_api_error"
        self._device_group = "diagnostics"

    @property
    def available(self) -> bool:
        return True

    @property
    def native_value(self) -> str | None:
        error = self.coordinator.last_api_error
        return error[:255] if error else None
