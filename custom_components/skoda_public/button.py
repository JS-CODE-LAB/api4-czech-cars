"""Diagnostic buttons."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SkodaConfigEntry, SkodaCoordinator
from .entity import SkodaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: SkodaConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([SkodaRefreshButton(entry.runtime_data)])


class SkodaRefreshButton(SkodaEntity, ButtonEntity):
    """Request an immediate refresh (consumes one API request)."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "refresh_vehicle_data"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: SkodaCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_refresh_vehicle_data"
        self._device_group = "diagnostics"

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()
