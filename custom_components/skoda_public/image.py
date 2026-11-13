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
from .localization import localized_path, KNOWN_FIELD_KEYS, field_translation_key

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
        new = [SkodaFieldImage(coordinator, path) for path in paths]
        known.update(paths)
        if new:
            async_add_entities(new)

    _discover()
    entry.async_on_unload(coordinator.async_add_listener(_discover))


class SkodaFieldImage(SkodaEntity, ImageEntity):
    """An API-provided vehicle picture represented as a native HA image."""

    _attr_content_type = "image/jpeg"

    def __init__(self, coordinator: SkodaCoordinator, path: str) -> None:
        super().__init__(coordinator)
        ImageEntity.__init__(self, coordinator.hass)
        self.field_path = path
        # Preserve the already-tested original image entity registry identity.
        self._attr_unique_id = f"{self._vin}_{path}_original"
        self._device_group = functional_group(path)
        self._attr_translation_key = field_translation_key(path, set(KNOWN_FIELD_KEYS.values())) if path in KNOWN_FIELD_KEYS else "original_api_field"
        self._attr_translation_placeholders = {
            "field_cs": localized_path(path, "cs"),
            "field_en": localized_path(path, "en")
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
                # A single StreamReader.read(n) may return only the first
                # network chunk, even when Content-Length is much larger.
                # Read to EOF while enforcing the maximum allowed size.
                chunks: list[bytes] = []
                total_bytes = 0
                async for chunk in response.content.iter_chunked(64 * 1024):
                    total_bytes += len(chunk)
                    if total_bytes > MAX_IMAGE_BYTES:
                        _LOGGER.warning("Vehicle image %s exceeds size limit", self.field_path)
                        return None
                    chunks.append(chunk)
                data = b"".join(chunks)
                if response.content_length is not None and len(data) != response.content_length:
                    _LOGGER.warning(
                        "Vehicle image %s incomplete: received %s of %s bytes",
                        self.field_path, len(data), response.content_length,
                    )
                    return None
                if len(data) > MAX_IMAGE_BYTES:
                    _LOGGER.warning("Vehicle image %s exceeds size limit", self.field_path)
                    return None
                self._attr_content_type = content_type
                return data
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            _LOGGER.warning("Vehicle image %s could not be loaded: %s", self.field_path, type(err).__name__)
            return None
