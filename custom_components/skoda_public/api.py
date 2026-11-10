"""Minimal async client for the MyŠkoda Public API."""
from __future__ import annotations

import asyncio
import json as json_lib
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import aiohttp

from homeassistant.util import dt as dt_util

from .const import API_BASE


class SkodaApiError(Exception):
    """Generic API error."""


class SkodaAuthError(SkodaApiError):
    """API key expired or not authorized."""


class SkodaRateLimitError(SkodaApiError):
    """Rate limit exceeded (429)."""

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


@dataclass
class ApiMeta:
    """Rate-limit and key-expiry information from response headers."""

    limit: int | None = None
    remaining: int | None = None
    reset: int | None = None
    key_expires_at: datetime | None = None


@dataclass
class ApiResult:
    """Result of an API call."""

    status: int
    body: Any
    meta: ApiMeta


def _int(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _parse_meta(headers: Any) -> ApiMeta:
    expires = headers.get("X-API-Key-Expires-At")
    return ApiMeta(
        limit=_int(headers.get("RateLimit-Limit")),
        remaining=_int(headers.get("RateLimit-Remaining")),
        reset=_int(headers.get("RateLimit-Reset")),
        key_expires_at=dt_util.parse_datetime(expires) if expires else None,
    )


class SkodaApiClient:
    """Client bound to one API key and one VIN."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str, vin: str) -> None:
        self._session = session
        self._api_key = api_key
        self.vin = vin

    async def async_request(
        self,
        method: str,
        path: str = "",
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> ApiResult:
        """Call /api/v1/vehicles/{vin}{path}."""
        url = f"{API_BASE}/api/v1/vehicles/{self.vin}{path}"
        headers = {"X-API-Key": self._api_key, "Accept": "application/json"}
        try:
            async with asyncio.timeout(30):
                async with self._session.request(
                    method, url, headers=headers, params=params, json=json
                ) as resp:
                    meta = _parse_meta(resp.headers)
                    text = await resp.text()
                    body: Any = None
                    if text:
                        try:
                            body = json_lib.loads(text)
                        except ValueError:
                            body = text
                    if resp.status >= 400:
                        raise self._to_error(resp.status, body, resp.headers)
                    return ApiResult(resp.status, body, meta)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise SkodaApiError(f"Communication error: {err}") from err

    async def async_get_vehicle(self) -> ApiResult:
        """Fetch the vehicle and its full current state."""
        return await self.async_request("GET")

    @staticmethod
    def _to_error(status: int, body: Any, headers: Any) -> SkodaApiError:
        problem = ""
        detail = f"HTTP {status}"
        if isinstance(body, dict):
            ptype = str(body.get("type") or "")
            if ptype and ptype != "about:blank":
                problem = ptype.rstrip("/").rsplit("/", 1)[-1]
            detail = str(body.get("detail") or body.get("title") or detail)
        message = f"{problem}: {detail}" if problem else detail

        if status == 401:
            return SkodaAuthError(message)
        if status == 403 and problem != "operation-not-authorized":
            return SkodaAuthError(message)
        if status == 429:
            return SkodaRateLimitError(message, _int(headers.get("Retry-After")))
        return SkodaApiError(message)
