"""Functional classification of API fields for documentation and entity naming.

Home Assistant does not support arbitrary device-page entity sections.
The group is exposed as an entity attribute instead of creating fake devices.
"""
from __future__ import annotations

GROUPS = ("battery", "charging", "vehicle_status", "climate", "engine",
          "location", "vehicle_info", "diagnostics")


def functional_group(path: str) -> str:
    """Classify a flattened vehicle field without depending on a specific model."""
    p = path.lower()
    if any(s in p for s in ("position", "latitude", "longitude", "parking")):
        return "location"
    if any(s in p for s in ("charging", "charger", "plug", "chargeprofile")):
        return "charging"
    if any(s in p for s in ("battery", "stateofcharge", "electricrange")):
        return "battery"
    if any(s in p for s in ("airconditioning", "climatisation", "climatization",
                            "auxiliaryheating", "activeventilation", "temperature")):
        return "climate"
    if any(s in p for s in ("fuel", "engine", "combustion", "oil")):
        return "engine"
    if any(s in p for s in ("door", "window", "lock", "light", "bonnet",
                            "hood", "trunk", "tailgate", "tyre", "tire")):
        return "vehicle_status"
    if any(s in p for s in ("vin", "model", "mileage", "odometer",
                            "registration", "production", "vehicle")):
        return "vehicle_info"
    return "vehicle_status"


def binary_device_class(path: str) -> str | None:
    """Return a HA BinarySensorDeviceClass value for unambiguous paths only."""
    p = path.lower()
    leaf = p.rsplit(".", 1)[-1]
    if any(k in leaf for k in ("locked", "lockstate")):
        return "lock"
    if "door" in p or "bonnet" in p or "hood" in p or "tailgate" in p or "trunk" in p:
        return "door"
    if "window" in p:
        return "window"
    if "plug" in p and "connected" in leaf:
        return "plug"
    if "light" in p:
        return "light"
    return None
