# Changelog

## 0.3.0
- Functional group attributes for discovered fields (no artificial subdevices).
- Manual refresh diagnostic button and last successful update timestamp.
- More descriptive binary sensor device classes for common vehicle fields.
- Charging limit marked as a configuration entity.
- Existing unique IDs retained for previously available entities.
- Vehicle-specific API fields continue to be discovered dynamically.

## 0.2.0
- Remote commands: charging start/stop, charging limit, air conditioning (climate), auxiliary heating, active ventilation.
- Dedicated Battery, Battery charging and Range sensors.
- Generic `skoda_public.request` service.
- Brand images (icon and logo) for Home Assistant 2026.3+.
- Platform modules are imported in the executor (no blocking-call warning).
- Renamed to "API 4 Czech Cars (public API)".

## 0.1.0
- Initial read-only version: all vehicle data exposed as sensors, binary sensors and a device tracker.
