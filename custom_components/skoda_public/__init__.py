"""Škoda Connected Vehicle (MyŠkoda Public API) integration."""
from __future__ import annotations

import importlib
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.typing import ConfigType

from .api import SkodaApiClient, SkodaApiError
from .const import CONF_VIN, DOMAIN, PLATFORMS, SERVICE_REQUEST
from .coordinator import SkodaConfigEntry, SkodaCoordinator
from .security import redact_sensitive
from .image_fields import is_image_field

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

REQUEST_SCHEMA = vol.Schema(
    {
        vol.Required("path"): cv.string,
        vol.Optional("method", default="POST"): vol.In(
            ["GET", "POST", "PUT", "PATCH", "DELETE"]
        ),
        vol.Optional("body"): vol.Any(dict, list),
        vol.Optional(CONF_VIN): cv.string,
        vol.Optional("refresh", default=False): cv.boolean,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the generic request service."""

    async def _handle_request(call: ServiceCall) -> dict[str, Any]:
        entries = [
            e
            for e in hass.config_entries.async_entries(DOMAIN)
            if e.state is ConfigEntryState.LOADED
        ]
        vin = call.data.get(CONF_VIN)
        if vin:
            entries = [e for e in entries if e.data[CONF_VIN].upper() == vin.upper()]
        if len(entries) != 1:
            raise HomeAssistantError(
                "Specify 'vin' – could not pick exactly one loaded vehicle"
            )
        coordinator: SkodaCoordinator = entries[0].runtime_data

        path: str = call.data["path"]
        if not path.startswith("/") or ".." in path or "://" in path:
            raise HomeAssistantError(
                "path must start with '/' and is relative to /api/v1/vehicles/{vin}"
            )
        try:
            result = await coordinator.client.async_request(
                call.data["method"], path, json=call.data.get("body")
            )
        except SkodaApiError as err:
            raise HomeAssistantError(redact_sensitive(str(err), coordinator.client._api_key, coordinator.vin, coordinator.config_entry.options.get("spin"))) from err
        if call.data["refresh"]:
            await coordinator.async_request_refresh()
        return {
            "status": result.status,
            "body": result.body,
            "ratelimit_remaining": result.meta.remaining,
        }

    hass.services.async_register(
        DOMAIN,
        SERVICE_REQUEST,
        _handle_request,
        schema=REQUEST_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SkodaConfigEntry) -> bool:
    client = SkodaApiClient(
        async_get_clientsession(hass), entry.data[CONF_API_KEY], entry.data[CONF_VIN]
    )
    coordinator = SkodaCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    # Import platform modules in the executor so HA does not import them inside the event loop.
    for platform in PLATFORMS:
        await hass.async_add_import_executor_job(
            importlib.import_module, f"{__name__}.{platform.value}"
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _remove_empty_vehicle_parent(hass, entry, coordinator.vin)
    _remove_legacy_processed_images(hass, entry, coordinator)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


def _remove_empty_vehicle_parent(
    hass: HomeAssistant, entry: SkodaConfigEntry, vin: str
) -> None:
    """Flatten legacy group hierarchy and remove only the empty parent device.

    The config entry itself remains named after the car. Never remove a parent
    that has entities attached to it (including user-created or future entities).
    """
    registry = dr.async_get(hass)
    parent = registry.async_get_device(identifiers={(DOMAIN, vin)})
    if parent is None or entry.entry_id not in parent.config_entries:
        return

    for device in list(registry.devices.values()):
        if (
            device.via_device_id == parent.id
            and entry.entry_id in device.config_entries
        ):
            registry.async_update_device(device.id, via_device_id=None)

    entities = er.async_get(hass)
    if any(entity.device_id == parent.id for entity in entities.entities.values()):
        return
    # Do not remove a shared device belonging to another config entry.
    if parent.config_entries == {entry.entry_id}:
        registry.async_remove_device(parent.id)


def _remove_legacy_processed_images(
    hass: HomeAssistant, entry: SkodaConfigEntry, coordinator: SkodaCoordinator
) -> None:
    """Remove only the obsolete processed-image entity registry entries.

    Original image entities retain their existing *_original unique IDs.
    """
    if coordinator.data is None:
        return
    registry = er.async_get(hass)
    for path, value in coordinator.data.flat.items():
        if not is_image_field(path, value):
            continue
        old_unique_id = f"{coordinator.vin}_{path}"
        entity_id = registry.async_get_entity_id("image", DOMAIN, old_unique_id)
        if entity_id is None:
            continue
        entity = registry.async_get(entity_id)
        if entity is not None and entity.config_entry_id == entry.entry_id:
            registry.async_remove(entity_id)


async def _async_options_updated(hass: HomeAssistant, entry: SkodaConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: SkodaConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
