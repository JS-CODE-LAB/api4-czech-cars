"""Device tracker for the parking position (any lat/lon pair in the response)."""
from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SkodaConfigEntry, SkodaCoordinator
from .entity import SkodaEntity, find_positions
from .localization import localized_path


async def async_setup_entry(
    hass: HomeAssistant, entry: SkodaConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    known: set[str] = set()

    @callback
    def _discover() -> None:
        if coordinator.data is None:
            return
        new = []
        for prefix, (lat, lon) in find_positions(coordinator.data.flat).items():
            if prefix not in known:
                known.add(prefix)
                new.append(SkodaTracker(coordinator, prefix, lat, lon))
        if new:
            async_add_entities(new)

    _discover()
    entry.async_on_unload(coordinator.async_add_listener(_discover))


class SkodaTracker(SkodaEntity, TrackerEntity):
    _attr_source_type = SourceType.GPS

    def __init__(
        self, coordinator: SkodaCoordinator, prefix: str, lat_path: str, lon_path: str
    ) -> None:
        super().__init__(coordinator)
        self._device_group = "location"
        self._lat_path = lat_path
        self._lon_path = lon_path
        self._attr_unique_id = f"{self._vin}_tracker_{prefix or 'vehicle'}"
        # Drop the trailing "coordinates"-style segment to get a readable name.
        self._attr_translation_key = "api_field"
        self._attr_translation_placeholders = {
            "field": localized_path(prefix, coordinator.hass.config.language) if prefix else ("Poloha" if coordinator.hass.config.language.startswith("cs") else "Position")
        }

    @property
    def latitude(self) -> float | None:
        value = self.coordinator.data.flat.get(self._lat_path)
        return float(value) if isinstance(value, (int, float)) else None

    @property
    def longitude(self) -> float | None:
        value = self.coordinator.data.flat.get(self._lon_path)
        return float(value) if isinstance(value, (int, float)) else None
