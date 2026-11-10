"""Config flow."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SkodaApiClient, SkodaApiError, SkodaAuthError
from .const import (
    CONF_AC_NO_EXT_POWER,
    CONF_AUX_DURATION,
    CONF_SCAN_INTERVAL,
    CONF_SPIN,
    CONF_VIN,
    DEFAULT_AC_NO_EXT_POWER,
    DEFAULT_AUX_DURATION,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)
from .coordinator import SkodaConfigEntry


class SkodaConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def _validate(self, api_key: str, vin: str) -> str:
        client = SkodaApiClient(async_get_clientsession(self.hass), api_key, vin)
        result = await client.async_get_vehicle()
        body = result.body if isinstance(result.body, dict) else {}
        return (body.get("vehicle") or {}).get("name") or vin

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            vin = user_input[CONF_VIN].strip().upper()
            api_key = user_input[CONF_API_KEY].strip()
            await self.async_set_unique_id(vin)
            self._abort_if_unique_id_configured()
            try:
                title = await self._validate(api_key, vin)
            except SkodaAuthError:
                errors["base"] = "invalid_auth"
            except SkodaApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=title, data={CONF_API_KEY: api_key, CONF_VIN: vin}
                )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_API_KEY): str, vol.Required(CONF_VIN): str}
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()
        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            try:
                await self._validate(api_key, entry.data[CONF_VIN])
            except SkodaAuthError:
                errors["base"] = "invalid_auth"
            except SkodaApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    entry, data={**entry.data, CONF_API_KEY: api_key}
                )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: SkodaConfigEntry) -> OptionsFlow:
        return SkodaOptionsFlow()


class SkodaOptionsFlow(OptionsFlow):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        opts = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=opts.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): vol.All(
                        vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=86400)
                    ),
                    vol.Optional(
                        CONF_AC_NO_EXT_POWER,
                        default=opts.get(CONF_AC_NO_EXT_POWER, DEFAULT_AC_NO_EXT_POWER),
                    ): bool,
                    vol.Optional(
                        CONF_AUX_DURATION,
                        default=opts.get(CONF_AUX_DURATION, DEFAULT_AUX_DURATION),
                    ): vol.All(vol.Coerce(int), vol.Range(min=60, max=7200)),
                    vol.Optional(
                        CONF_SPIN, default=opts.get(CONF_SPIN, "")
                    ): str,
                }
            ),
        )
