"""Climate entity: start/stop air conditioning (pre-conditioning)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_AC_NO_EXT_POWER, DEFAULT_AC_NO_EXT_POWER
from .coordinator import SkodaConfigEntry, SkodaCoordinator
from .entity import SkodaControlEntity

STATE_PATH = "airConditioning.state"
TEMP_PATH = "airConditioning.targetTemperature.value"
UNIT_PATH = "airConditioning.targetTemperature.unit"


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
        if "airConditioning" in coordinator.data.vehicle:
            added = True
            async_add_entities([SkodaClimate(coordinator)])

    _discover()
    entry.async_on_unload(coordinator.async_add_listener(_discover))


class SkodaClimate(SkodaControlEntity, ClimateEntity):
    """Air conditioning.

    The API has no 'set temperature only' call: a temperature can only be sent
    together with the start command. While the A/C is off, changing the target
    just stores it locally and it is used the next time the A/C is started.
    """

    _attr_name = "Air conditioning"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT_COOL]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_min_temp = 16
    _attr_max_temp = 30
    _attr_target_temperature_step = 0.5
    _enable_turn_on_off_backwards_compatibility = False

    def __init__(self, coordinator: SkodaCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_climate_air_conditioning"
        self._device_group = "climate"
        self._pending_target: float | None = None

    def _reported_state(self) -> str | None:
        value = self.coordinator.data.flat.get(STATE_PATH)
        return value.upper() if isinstance(value, str) else None

    @property
    def hvac_mode(self) -> HVACMode | None:
        optimistic = self._get_optimistic()
        if optimistic is not None:
            return optimistic
        state = self._reported_state()
        if state is None:
            return None
        return HVACMode.OFF if state in ("OFF", "UNKNOWN") else HVACMode.HEAT_COOL

    @property
    def target_temperature(self) -> float | None:
        if self._pending_target is not None:
            return self._pending_target
        value = self.coordinator.data.flat.get(TEMP_PATH)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return None
        unit = self.coordinator.data.flat.get(UNIT_PATH)
        if isinstance(unit, str) and unit.upper() == "FAHRENHEIT":
            return round((value - 32) * 5 / 9 * 2) / 2
        return float(value)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"api_state": self._reported_state()}

    async def _start(self, temperature: float | None) -> None:
        body: dict[str, Any] = {
            "airConditioningWithoutExternalPower": self.coordinator.config_entry.options.get(
                CONF_AC_NO_EXT_POWER, DEFAULT_AC_NO_EXT_POWER
            )
        }
        if temperature is not None:
            body["targetTemperature"] = {"value": temperature, "unit": "CELSIUS"}
        await self.coordinator.async_command("POST", "/air-conditioning/start", json=body)
        self._pending_target = None
        self._set_optimistic(HVACMode.HEAT_COOL)

    async def _stop(self) -> None:
        await self.coordinator.async_command("POST", "/air-conditioning/stop")
        self._set_optimistic(HVACMode.OFF)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self._stop()
        else:
            await self._start(self.target_temperature)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temperature = kwargs.get(ATTR_TEMPERATURE)
        mode = kwargs.get(ATTR_HVAC_MODE)
        if mode == HVACMode.OFF:
            await self._stop()
            return
        if temperature is None:
            return
        if mode == HVACMode.HEAT_COOL or self.hvac_mode == HVACMode.HEAT_COOL:
            await self._start(float(temperature))
        else:
            # A/C is off: remember the target, do not start the car's A/C.
            self._pending_target = float(temperature)
            self.async_write_ha_state()

    async def async_turn_on(self) -> None:
        await self._start(self.target_temperature)

    async def async_turn_off(self) -> None:
        await self._stop()
