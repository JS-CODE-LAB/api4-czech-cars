# Changelog

## 0.3.3 (unreleased)
- Translate dynamic entity names per user profile using Czech/English translation placeholders (not global HA language).
- Use stable English default names for functional devices, whose registry names are not user-localized.
- Add locale fallback tests and preserve stable entity and device identifiers.

## 0.3.2
- Retain only the unmodified original vehicle image entity; remove temporary image diagnostics and obsolete light-background image entity from the registry.
- Fix truncated vehicle renders by consuming the full HTTP response stream in bounded chunks and verifying Content-Length before decoding.
- Remove the redundant empty vehicle device from the grouped device list while retaining the vehicle config entry heading.
- Flatten functional groups into independent devices and migrate existing registry links without changing entity unique IDs.
- Translate entity names to Czech in Czech Home Assistant installations; keep English names for English installations.
- Add native Home Assistant image entities for image URLs returned by the API.
- Keep existing unique IDs for ordinary fields and control entities; image fields move from sensor to image domain.
- Add standalone Czech localization and image classification tests.
- Existing manually customized entity names are not overwritten; inspect the entity registry after upgrading.

## 0.3.1
- Organize entities into virtual child devices linked to the parent vehicle via via_device.
- Separate charging profiles, charging, battery, climate, doors, windows, lights,
  counters, powertrain, location, settings, vehicle information and diagnostics.
- Preserve entity unique IDs; child devices appear only for available entities.
- Add a last API polling error diagnostic sensor.
- Extend functional classification tests.
- Move the Range (km) sensor to Counters and consumption alongside the odometer.
- Clarify upgrade guidance, API safety, and privacy notices.
- Default air conditioning without external power to disabled for new installations.
- Device-based automations may need checking after entities move between devices.

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
