"""Number entity: charging limit (target state of charge)."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SkodaConfigEntry, SkodaCoordinator
from .entity import SkodaControlEntity

LIMIT_PATH = "charging.settings.targetStateOfChargeInPercent"


async def async_setup_entry(
    hass: HomeAssistant, entry: SkodaConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    added = False

    @callback
    def _discover() -> None:
        nonlocal added
        if added or coordinator.data is None:
            return
        if "charging" in coordinator.data.vehicle:
            added = True
            async_add_entities([SkodaChargingLimit(coordinator)])

    _discover()
    entry.async_on_unload(coordinator.async_add_listener(_discover))


class SkodaChargingLimit(SkodaControlEntity, NumberEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "charging_limit"
    _attr_icon = "mdi:battery-charging-high"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER
    # Vehicles typically accept 50-100 % in steps of 10 (API spec allows 1-100).
    _attr_native_min_value = 50
    _attr_native_max_value = 100
    _attr_native_step = 10

    def __init__(self, coordinator: SkodaCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_number_charging_limit"
        self._device_group = "charging"

    @property
    def native_value(self) -> float | None:
        optimistic = self._get_optimistic()
        if optimistic is not None:
            return optimistic
        value = self.coordinator.data.flat.get(LIMIT_PATH)
        return float(value) if isinstance(value, (int, float)) else None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_command(
            "PUT",
            "/charging/limit",
            json={"targetStateOfChargeInPercent": int(value)},
        )
        self._set_optimistic(float(value), seconds=120)
