"""Constants for the Škoda Public API integration."""
from homeassistant.const import Platform

DOMAIN = "skoda_public"

CONF_VIN = "vin"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_SPIN = "spin"
CONF_AUX_DURATION = "aux_heating_duration"
CONF_AC_NO_EXT_POWER = "ac_without_external_power"

# API limit is 20 requests/hour per VIN (may change). 600 s = 6 req/h, which
# leaves headroom for commands (each command also triggers one delayed refresh).
DEFAULT_SCAN_INTERVAL = 600
MIN_SCAN_INTERVAL = 300
DEFAULT_AUX_DURATION = 600
DEFAULT_AC_NO_EXT_POWER = False

API_BASE = "https://public.api.connect.skoda-auto.cz"

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.CLIMATE,
    Platform.BUTTON,
]

SERVICE_REQUEST = "request"
