"""Switches for remote commands: charging, auxiliary heating, active ventilation."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_AUX_DURATION, CONF_SPIN, DEFAULT_AUX_DURATION
from .coordinator import SkodaConfigEntry, SkodaCoordinator
from .entity import SkodaControlEntity


def _aux_body(coordinator: SkodaCoordinator) -> dict[str, Any]:
    opts = coordinator.config_entry.options
    spin = opts.get(CONF_SPIN)
    if not spin:
        raise HomeAssistantError(
            "Auxiliary heating needs your S-PIN: set it in the integration options."
        )
    return {
        "spin": spin,
        "durationInSeconds": int(opts.get(CONF_AUX_DURATION, DEFAULT_AUX_DURATION)),
        "startMode": "HEATING",
    }


def _not_off(value: Any) -> bool | None:
    if not isinstance(value, str):
        return None
    return value.upper() not in ("OFF", "UNKNOWN")


@dataclass(frozen=True)
class SwitchDef:
    key: str
    name: str
    icon: str
    section: str  # top-level key of the vehicle object; switch exists only if present
    state_path: str
    is_on: Callable[[Any], bool | None]
    start_path: str
    stop_path: str
    body: Callable[[SkodaCoordinator], dict[str, Any] | None] | None = None


SWITCHES = (
    SwitchDef(
        key="charging",
        name="Charging",
        icon="mdi:ev-station",
        section="charging",
        state_path="charging.status.state",
        is_on=lambda v: v.upper() == "CHARGING" if isinstance(v, str) else None,
        start_path="/charging/start",
        stop_path="/charging/stop",
    ),
    SwitchDef(
        key="auxiliary_heating",
        name="Auxiliary heating",
        icon="mdi:radiator",
        section="auxiliaryHeating",
        state_path="auxiliaryHeating.state",
        is_on=_not_off,
        start_path="/auxiliary-heating/start",
        stop_path="/auxiliary-heating/stop",
        body=_aux_body,
    ),
    SwitchDef(
        key="active_ventilation",
        name="Active ventilation",
        icon="mdi:fan",
        section="activeVentilation",
        state_path="activeVentilation.state",
        is_on=_not_off,
        start_path="/active-ventilation/start",
        stop_path="/active-ventilation/stop",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: SkodaConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    known: set[str] = set()

    @callback
    def _discover() -> None:
        if coordinator.data is None:
            return
        new = [
            SkodaCommandSwitch(coordinator, d)
            for d in SWITCHES
            if d.key not in known and d.section in coordinator.data.vehicle
        ]
        known.update(e.entity_def.key for e in new)
        if new:
            async_add_entities(new)

    _discover()
    entry.async_on_unload(coordinator.async_add_listener(_discover))


class SkodaCommandSwitch(SkodaControlEntity, SwitchEntity):
    def __init__(self, coordinator: SkodaCoordinator, definition: SwitchDef) -> None:
        super().__init__(coordinator)
        self.entity_def = definition
        self._attr_unique_id = f"{self._vin}_switch_{definition.key}"
        self._attr_name = definition.name
        self._attr_icon = definition.icon

    @property
    def is_on(self) -> bool | None:
        optimistic = self._get_optimistic()
        if optimistic is not None:
            return optimistic
        return self.entity_def.is_on(
            self.coordinator.data.flat.get(self.entity_def.state_path)
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        d = self.entity_def
        body = d.body(self.coordinator) if d.body else None
        await self.coordinator.async_command("POST", d.start_path, json=body)
        self._set_optimistic(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_command("POST", self.entity_def.stop_path)
        self._set_optimistic(False)
