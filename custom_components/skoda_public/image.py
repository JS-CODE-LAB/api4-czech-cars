"""Image entities for URLs returned by the vehicle API."""
from __future__ import annotations

import logging
from datetime import datetime
from urllib.parse import urlsplit

import aiohttp

from homeassistant.components.image import ImageEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SkodaConfigEntry, SkodaCoordinator
from .entity import SkodaEntity
from .groups import functional_group
from .image_fields import is_image_field
from .image_diagnostics import inspect_image
from .image_processing import prepare_vehicle_image
from .localization import localized_path

_LOGGER = logging.getLogger(__name__)
MAX_IMAGE_BYTES = 8 * 1024 * 1024


async def async_setup_entry(
    hass: HomeAssistant, entry: SkodaConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    known: set[str] = set()

    @callback
    def _discover() -> None:
        if coordinator.data is None:
            return
        paths = [
            path for path, value in coordinator.data.flat.items()
            if path not in known and is_image_field(path, value)
        ]
        new = [
            SkodaFieldImage(coordinator, path, original=original)
            for path in paths for original in (False, True)
        ]
        known.update(paths)
        if new:
            async_add_entities(new)

    _discover()
    entry.async_on_unload(coordinator.async_add_listener(_discover))


class SkodaFieldImage(SkodaEntity, ImageEntity):
    """An API-provided vehicle picture represented as a native HA image."""

    _attr_content_type = "image/jpeg"

    def __init__(self, coordinator: SkodaCoordinator, path: str, *, original: bool = False) -> None:
        super().__init__(coordinator)
        ImageEntity.__init__(self, coordinator.hass)
        self.field_path = path
        self._original = original
        self._attr_unique_id = f"{self._vin}_{path}" + ("_original" if original else "")
        self._device_group = functional_group(path)
        self._attr_translation_key = "original_api_field" if original else "api_field"
        self._attr_translation_placeholders = {
            "field": localized_path(path, coordinator.hass.config.language)
        }
        self._attr_image_last_updated = datetime.now().astimezone()

    @property
    def image_last_updated(self) -> datetime:
        return self.coordinator.last_successful_update or self._attr_image_last_updated

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {"api_path": self.field_path, "functional_group": self._device_group}

    async def async_image(self) -> bytes | None:
        """Fetch the current picture without exposing its URL as sensor state."""
        if self.coordinator.data is None:
            return None
        url = self.coordinator.data.flat.get(self.field_path)
        if not is_image_field(self.field_path, url):
            _LOGGER.debug("Vehicle image unavailable for API path %s: missing or invalid HTTPS image URL", self.field_path)
            return None
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname:
            return None
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                url, allow_redirects=False, timeout=aiohttp.ClientTimeout(total=20)
            ) as response:
                if response.status != 200:
                    _LOGGER.warning("Vehicle image %s could not be fetched: HTTP %s", self.field_path, response.status)
                    return None
                content_type = response.headers.get("Content-Type", "").split(";", 1)[0].lower()
                if not content_type.startswith("image/"):
                    _LOGGER.warning("Vehicle image %s has unsupported content type %s", self.field_path, content_type)
                    return None
                if response.content_length and response.content_length > MAX_IMAGE_BYTES:
                    _LOGGER.warning("Vehicle image %s exceeds size limit", self.field_path)
                    return None
                data = await response.content.read(MAX_IMAGE_BYTES + 1)
                if len(data) > MAX_IMAGE_BYTES:
                    _LOGGER.warning("Vehicle image %s exceeds size limit", self.field_path)
                    return None
                self._attr_content_type = content_type
                if _LOGGER.isEnabledFor(logging.DEBUG):
                    info = inspect_image(data)
                    _LOGGER.debug(
                        "Vehicle image diagnostic path=%s status=%s "
                        "content_type=%s bytes=%s format=%s dimensions=%sx%s "
                        "alpha=%s declared_length=%s",
                        self.field_path, response.status, content_type,
                        info["bytes"], info["format"], info["width"],
                        info["height"], info["alpha"],
                        response.content_length,
                    )
                if self._original:
                    return data
                try:
                    processed, metadata = await self.hass.async_add_executor_job(
                        prepare_vehicle_image, data
                    )
                    self._attr_content_type = "image/png"
                    _LOGGER.debug(
                        "Vehicle image processing path=%s original_size=%s "
                        "visible_bounds=%s visible_size=%s output_size=%s",
                        self.field_path, metadata["source_size"],
                        metadata["visible_bounds"], metadata["visible_size"],
                        metadata["output_size"],
                    )
                    return processed
                except (OSError, ValueError) as err:
                    _LOGGER.warning(
                        "Vehicle image processing failed for %s: %s; using original",
                        self.field_path, type(err).__name__,
                    )
                    return data
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            _LOGGER.warning("Vehicle image %s could not be loaded: %s", self.field_path, type(err).__name__)
            return None
