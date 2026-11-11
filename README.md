<p align="center">
  <img src="https://raw.githubusercontent.com/JS-CODE-LAB/api4-czech-cars/main/custom_components/skoda_public/brand/logo%402x.png" alt="API 4 Czech Cars" width="320">
</p>

# API 4 Czech Cars (public API) for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Home Assistant integration for connected ŠKODA vehicles, built on the official
[MyŠkoda Public API](https://public.api.connect.skoda-auto.cz/docs). Čeština: [README.cs.md](README.cs.md).

> **Unofficial community project.** Not affiliated with or endorsed by ŠKODA AUTO a.s., the Volkswagen
> Group, Home Assistant or HACS. Remote commands act on a real vehicle – read the
> [DISCLAIMER](DISCLAIMER.md) (including the safety notes) before use.

## Features
Everything the API returns for your vehicle becomes an entity, and new fields appear automatically:

| Platform | What you get |
|---|---|
| `sensor` | Battery level, **range (km)**, odometer, fuel, charging status and settings, charging profiles, air conditioning, doors/windows/lights state, … (units and device classes are derived from field names) |
| `binary_sensor` | All YES/NO fields (e.g. doors locked), **battery charging** |
| `device_tracker` | Parking position |
| `switch` | Charging start/stop, auxiliary heating, active ventilation |
| `number` | Charging limit (50–100 %, step 10) |
| `climate` | Air conditioning on/off and target temperature |
| diagnostics | Remaining API requests, API key expiry, omitted data parts, last successful update, last API error, manual refresh button |

Control entities only appear when your vehicle reports the matching feature. The battery level and charging
icon are shown at the top of the device page.

A service `skoda_public.request` can send any request to `/api/v1/vehicles/{vin}{path}` (for example
features without a dedicated entity).

## Entity organization (0.3.1)
Dynamic sensors and binary sensors have a `functional_group` attribute, one of:
`battery`, `charging`, `vehicle_status`, `climate`, `engine`,
`location`, `vehicle_info`, `diagnostics`.
In v0.3.1 entities are attached to virtual child devices linked to the
main vehicle with Home Assistant's via_device relationship. Only groups
containing entities appear. Entity unique IDs are preserved, but their device
association changes. Review device-based automations after upgrading. Manual refresh consumes an
API request. New fields are discovered as the vehicle API returns them.

## Requirements
- Home Assistant **2026.3.0** or newer (brand images are shipped inside the integration).
- A ŠKODA vehicle with an active MyŠkoda connectivity subscription and a **MyŠkoda API key** for that vehicle
  (create it in the MyŠkoda app: <https://go.skoda.eu/api-keys>).

## Installation

### HACS (custom repository)
1. HACS → ⋮ → **Custom repositories**.
2. Repository: `https://github.com/JS-CODE-LAB/api4-czech-cars`, type **Integration** → Add.
3. Find **API 4 Czech Cars (public API)** in HACS → **Download**.
4. Restart Home Assistant.

### Manual
Copy `custom_components/skoda_public` to `<config>/custom_components/` and restart.

## Setup
Settings → Devices & services → **Add integration** → *API 4 Czech Cars (public API)*, then enter the API
key and the VIN. Adding the same vehicle twice is not possible; add one entry per vehicle.

### Options
| Option | Meaning |
|---|---|
| Update interval | Seconds between polls (default 600, minimum 300). |
| Air conditioning without external power | Allow starting A/C when the car is not plugged in. |
| Auxiliary heating duration | Seconds the heater runs (default 600). |
| S-PIN | Required by the API for auxiliary heating. Stored unencrypted by Home Assistant. |

## Good to know
- **Rate limit:** the API allows about 20 requests per hour per vehicle. Every command also triggers one extra
  refresh ~30 s later.
- **Air conditioning temperature:** the API has no "set temperature only" call. While the A/C is off, changing the
  target only stores it in Home Assistant and uses it the next time you turn the A/C on. While it is running,
  changing it sends a new start command.
- **Vehicle may refuse commands** (not supported, offline, low battery, …); the reason is shown in Home Assistant.
- Not available as entities: changing the charging mode and editing charging profiles (use the service).
- Which data exists depends on the vehicle; unsupported parts are omitted by the API.

## Troubleshooting
- *Authentication failed / reauth:* the API key expired or does not belong to the VIN – create a new key and
  enter it when Home Assistant asks. The diagnostic sensor *API key expires at* helps you to renew it in time.
- *Too many requests (429):* increase the update interval.
- Report bugs via [Issues](../../issues) and **remove VIN, API key, S-PIN and GPS position** first.

## Privacy
Data flows only between your Home Assistant and ŠKODA's API. There is no telemetry. Credentials and the S-PIN are
stored in Home Assistant's configuration storage (not encrypted, included in backups). Vehicle position ends up in
your Home Assistant history unless you exclude it.

## Credits
Endpoint details were cross-checked with the open-source Python library
[skoda-public-api](https://github.com/mobility-lab-vsb/skoda-public-api) and the official API documentation.
No code from it is included.

## License
[MIT](LICENSE) – see also the [DISCLAIMER](DISCLAIMER.md). Trademarks belong to their respective owners.
