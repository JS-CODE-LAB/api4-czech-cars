"""Stable functional grouping for Škoda API fields.

Groups are virtual Home Assistant devices linked to one parent vehicle.
A group is created only when at least one entity is assigned to it.
"""
from __future__ import annotations

GROUP_NAMES = {
    "battery": "Baterie",
    "charging": "Nabíjení",
    "charging_profiles": "Nabíjecí profily",
    "climate": "Klimatizace a topení",
    "doors": "Dveře a zámky",
    "windows": "Okna",
    "lights": "Osvětlení",
    "counters": "Počítadla a spotřeba",
    "powertrain": "Pohon a palivo",
    "location": "Poloha a parkování",
    "settings": "Nastavení",
    "vehicle_info": "Informace o vozidle",
    "vehicle_status": "Ostatní stavy vozidla",
    "diagnostics": "Diagnostika",
}
GROUPS = tuple(GROUP_NAMES)


def functional_group(path: str) -> str:
    """Choose a stable group based on an API path; order is significant."""
    p = path.lower()
    leaf = p.rsplit(".", 1)[-1]
    if any(k in p for k in ("chargeprofile", "chargingprofile", "chargingprofiles",
                            "chargingprofilesettings", "departuretimer",
                            "preferredcharging", "charginglocation")):
        return "charging_profiles"
    if any(k in p for k in ("position", "latitude", "longitude", "parking", "gps")):
        return "location"
    if any(k in p for k in ("window", "sunroof", "roofwindow")):
        return "windows"
    if any(k in p for k in ("door", "lock", "bonnet", "hood", "trunk", "tailgate")):
        return "doors"
    if any(k in p for k in ("light", "lamp", "headlight")):
        return "lights"
    if any(k in p for k in ("odometer", "mileage", "tripmeter", "distancecovered",
                            "consumption", "averageconsumption", "totaldistance",
                            "drivingtime", "operatinghours", "counter")):
        return "counters"
    if any(k in p for k in ("airconditioning", "climatisation", "climatization",
                            "auxiliaryheating", "activeventilation", "heating",
                            "ventilation", "interiortemperature")):
        return "climate"
    if any(k in p for k in ("charging", "charger", "plug", "chargecurrent")):
        return "charging"
    if any(k in p for k in ("battery", "stateofcharge", "electricrange")):
        return "battery"
    if any(k in p for k in ("fuel", "engine", "combustion", "oil", "powertrain")):
        return "powertrain"
    if any(k in p for k in ("settings", "configuration", "preferences")):
        return "settings"
    if any(k in p for k in ("vin", "model", "registration", "production",
                            "vehicleinfo", "vehicledata")):
        return "vehicle_info"
    return "vehicle_status"


def binary_device_class(path: str) -> str | None:
    """Assign device classes only where the boolean's meaning is clear."""
    p = path.lower()
    leaf = p.rsplit(".", 1)[-1]
    if any(k in leaf for k in ("locked", "lockstate")):
        return "lock"
    if any(k in p for k in ("door", "bonnet", "hood", "tailgate", "trunk")):
        return "door"
    if "window" in p:
        return "window"
    if "plug" in p and "connected" in leaf:
        return "plug"
    if "light" in p:
        return "light"
    return None
