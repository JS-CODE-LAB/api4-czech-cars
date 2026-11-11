"""Data update coordinator."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.util import dt as dt_util
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    ApiMeta,
    ApiResult,
    SkodaApiClient,
    SkodaApiError,
    SkodaAuthError,
    SkodaRateLimitError,
)
from .const import CONF_SCAN_INTERVAL, CONF_VIN, CONF_SPIN, DEFAULT_SCAN_INTERVAL, DOMAIN
from .security import redact_sensitive

_LOGGER = logging.getLogger(__name__)

# Top-level identity fields that live on the device, not as entities.
EXCLUDED_PATHS = {"vin", "name"}

type SkodaConfigEntry = ConfigEntry[SkodaCoordinator]


def flatten(obj: Any, prefix: str = "") -> dict[str, Any]:
    """Flatten nested JSON into {'a.b.0.c': scalar}. None values are skipped."""
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            out.update(flatten(value, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            out.update(flatten(value, f"{prefix}.{idx}" if prefix else str(idx)))
    elif obj is not None and prefix:
        out[prefix] = obj
    return out


@dataclass
class SkodaData:
    """Parsed API response."""

    vehicle: dict[str, Any]
    errors: list[Any]
    flat: dict[str, Any]
    meta: ApiMeta


class SkodaCoordinator(DataUpdateCoordinator[SkodaData]):
    """Polls GET /api/v1/vehicles/{vin}."""

    config_entry: SkodaConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: SkodaConfigEntry, client: SkodaApiClient
    ) -> None:
        interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.data[CONF_VIN]}",
            update_interval=timedelta(seconds=interval),
            config_entry=entry,
        )
        self.client = client
        self.vin: str = entry.data[CONF_VIN]
        self._refresh_cancel = None
        self.last_successful_update: datetime | None = None
        self.last_api_error: str | None = None

    def _safe_error(self, err: Exception) -> str:
        """Hide configured credentials and VIN in diagnostic errors."""
        return redact_sensitive(
            str(err),
            self.client._api_key,
            self.vin,
            self.config_entry.options.get(CONF_SPIN),
        )

    async def async_command(
        self, method: str, path: str, json: Any = None
    ) -> ApiResult:
        """Send a remote command and schedule one refresh to pick up the new state."""
        try:
            result = await self.client.async_request(method, path, json=json)
        except SkodaAuthError as err:
            self.config_entry.async_start_reauth(self.hass)
            raise HomeAssistantError(f"API key rejected: {self._safe_error(err)}") from err
        except SkodaApiError as err:
            raise HomeAssistantError(self._safe_error(err)) from err
        self.async_schedule_delayed_refresh()
        return result

    @callback
    def async_schedule_delayed_refresh(self, delay: int = 30) -> None:
        """Refresh once, shortly after a command (replaces any pending one)."""
        if self._refresh_cancel is not None:
            self._refresh_cancel()

        async def _refresh(_now: Any) -> None:
            self._refresh_cancel = None
            await self.async_request_refresh()

        self._refresh_cancel = async_call_later(self.hass, delay, _refresh)

    async def async_shutdown(self) -> None:
        if self._refresh_cancel is not None:
            self._refresh_cancel()
            self._refresh_cancel = None
        await super().async_shutdown()

    async def _async_update_data(self) -> SkodaData:
        try:
            result = await self.client.async_get_vehicle()
        except SkodaAuthError as err:
            self.last_api_error = self._safe_error(err)
            raise ConfigEntryAuthFailed(self._safe_error(err)) from err
        except SkodaRateLimitError as err:
            self.last_api_error = str(err)
            raise UpdateFailed(
                f"Rate limit exceeded (retry after {err.retry_after}s): {self._safe_error(err)}"
            ) from err
        except SkodaApiError as err:
            self.last_api_error = str(err)
            raise UpdateFailed(self._safe_error(err)) from err

        body = result.body
        if not isinstance(body, dict) or not isinstance(body.get("vehicle"), dict):
            self.last_api_error = "Unexpected response format"
            raise UpdateFailed("Unexpected response format")

        vehicle = body["vehicle"]
        errors = body.get("errors") or []
        flat = {
            k: v for k, v in flatten(vehicle).items() if k not in EXCLUDED_PATHS
        }
        self.last_api_error = None
        self.last_successful_update = dt_util.utcnow()
        return SkodaData(vehicle=vehicle, errors=errors, flat=flat, meta=result.meta)
