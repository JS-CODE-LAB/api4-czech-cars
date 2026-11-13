"""Localized labels for API paths not known at integration build time.

Static entities use Home Assistant translation keys. Dynamic API fields use
a translated name template and these language-aware path labels.
"""
from __future__ import annotations

import re

CS = {
    "licenseplate": "registrační značka", "registrationplate": "registrační značka",
    "operations": "operace", "operation": "operace",
    "car": "vozidlo", "captured": "pořízení údajů",
    "render": "vizualizace vozidla", "renderurl": "obrázek vozidla",
    "vehiclerenderurl": "obrázek vozidla",
    "vehicle": "vozidlo", "vehicles": "vozidla", "status": "stav",
    "state": "stav", "charging": "nabíjení", "charge": "nabití",
    "battery": "baterie", "batterylevel": "úroveň baterie",
    "stateofcharge": "stav nabití", "stateofchargeinpercent": "stav nabití (%)",
    "targetstateofchargeinpercent": "cílové nabití (%)",
    "soc": "stav nabití", "range": "dojezd", "electricrange": "elektrický dojezd",
    "remainingrange": "zbývající dojezd", "odometer": "stav tachometru",
    "mileage": "nájezd", "tripmeter": "denní počítadlo",
    "distance": "vzdálenost", "distancecovered": "ujetá vzdálenost",
    "consumption": "spotřeba", "averageconsumption": "průměrná spotřeba",
    "totaldistance": "celková vzdálenost", "power": "výkon",
    "voltage": "napětí", "current": "proud", "temperature": "teplota",
    "outside": "venkovní", "inside": "vnitřní", "interior": "interiér",
    "exterior": "exteriér", "ambient": "okolní", "target": "cílová",
    "targettemperature": "cílová teplota", "airconditioning": "klimatizace",
    "auxiliaryheating": "nezávislé topení", "activeventilation": "aktivní větrání",
    "heating": "topení", "ventilation": "větrání", "climate": "klima",
    "doors": "dveře", "door": "dveře", "windows": "okna", "window": "okno",
    "front": "přední", "rear": "zadní", "left": "levé", "right": "pravé",
    "frontleft": "přední levé", "frontright": "přední pravé",
    "rearleft": "zadní levé", "rearright": "zadní pravé",
    "trunk": "kufr", "bonnet": "kapota", "hood": "kapota",
    "tailgate": "víko kufru", "lock": "zámek", "locked": "zamčeno",
    "unlocked": "odemčeno", "open": "otevřeno", "closed": "zavřeno",
    "lights": "světla", "light": "světlo", "lowbeam": "potkávací světla",
    "highbeam": "dálková světla", "parkinglights": "obrysová světla",
    "position": "poloha", "parking": "parkování", "latitude": "zeměpisná šířka",
    "longitude": "zeměpisná délka", "coordinates": "souřadnice",
    "address": "adresa", "location": "poloha", "fuel": "palivo",
    "fuellevel": "hladina paliva", "engine": "motor", "oil": "olej",
    "settings": "nastavení", "configuration": "konfigurace",
    "enabled": "povoleno", "active": "aktivní", "available": "dostupné",
    "connected": "připojeno", "plug": "konektor", "plugged": "zapojeno",
    "connector": "konektor", "cable": "kabel", "remaining": "zbývající",
    "time": "čas", "duration": "doba trvání", "start": "začátek",
    "end": "konec", "departure": "odjezd", "arrival": "příjezd",
    "estimated": "odhadovaný", "last": "poslední", "updated": "aktualizováno",
    "update": "aktualizace", "timestamp": "časové razítko",
    "name": "název", "model": "model", "vin": "VIN",
    "production": "výroba", "year": "rok", "registration": "registrace",
    "color": "barva", "colour": "barva", "image": "obrázek",
    "picture": "obrázek", "photo": "fotografie", "thumbnail": "náhled",
    "url": "URL", "uri": "URI", "icon": "ikona",
    "profile": "profil", "profiles": "profily", "chargingprofiles": "nabíjecí profily",
    "mode": "režim", "type": "typ", "value": "hodnota", "unit": "jednotka",
    "percent": "procenta", "inpercent": "(%)", "inkm": "(km)",
    "inmeters": "(m)", "inkwh": "(kWh)", "inkw": "(kW)",
    "inminutes": "(min)", "inseconds": "(s)", "incelsius": "(°C)",
    "inliters": "(l)", "speed": "rychlost", "pressure": "tlak",
    "health": "stav zdraví", "capacity": "kapacita", "maximum": "maximum",
    "minimum": "minimum", "max": "maximum", "min": "minimum",
    "total": "celkem", "average": "průměr", "is": "je", "has": "má",
    "in": "v", "of": "", "the": "", "data": "data", "error": "chyba",
    "errors": "chyby", "request": "požadavek", "requests": "požadavky",
}


def localized_path(path: str, language: str) -> str:
    """Readable path label; Czech for cs locales, English otherwise."""
    if (language or "").lower().replace("_", "-").split("-", 1)[0] != "cs":
        return humanize_path(path)
    parts = []
    for segment in path.split("."):
        if segment.isdigit():
            parts.append(str(int(segment) + 1))
            continue
        words = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", segment).replace("_", " ").split()
        key = segment.replace("_", "").lower()
        if key in CS:
            parts.append(CS[key])
        else:
            parts.extend(CS.get(word.lower(), word.lower()) for word in words)
    result = " ".join(part for part in parts if part).strip()
    if result.lower().startswith("operace ") and result.lower().endswith(" název"):
        result = result[:-6] + " – název"
    if path.lower() == "status.carcaptured.timestamp":
        return "Čas pořízení údajů o vozidle"
    return result[:1].upper() + result[1:] if result else path


def humanize_path(path: str) -> str:
    parts = []
    for segment in path.split("."):
        if segment.isdigit():
            parts.append(str(int(segment) + 1))
        else:
            parts.append(re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", segment).replace("_", " ").lower())
    text = " ".join(parts)
    return text[:1].upper() + text[1:]


# Stable translation keys for known API fields. Unknown fields retain an
# English fallback; never derive translation keys from arbitrary API paths.
KNOWN_FIELD_KEYS = {
    "airConditioning.state": "air_conditioning_state",
    "airConditioning.targetTemperature.unit": "air_conditioning_target_temperature_unit",
    "airConditioning.targetTemperature.value": "air_conditioning_target_temperature_value",
    "airConditioning.carCapturedTimestamp": "air_conditioning_car_captured_timestamp",
    "charging.status.battery.stateOfChargeInPercent": "charging_battery_soc",
    "charging.status.state": "charging_state",
    "status.carCaptured.timestamp": "vehicle_capture_timestamp",
}


KNOWN_FIELD_KEYS.update({
    "charging.carCapturedTimestamp": "field_charging_car_captured_timestamp",
    "charging.isVehicleInSavedLocation": "field_charging_is_vehicle_in_saved_location",
    "charging.settings.availableChargingModes": "field_charging_settings_available_charging_modes",
    "charging.settings.batteryCareModeTarget": "field_charging_settings_battery_care_mode_target",
    "charging.settings.chargingCareMode": "field_charging_settings_charging_care_mode",
    "charging.settings.maxChargeCurrent": "field_charging_settings_max_charge_current",
    "charging.settings.preferredChargeMode": "field_charging_settings_preferred_charge_mode",
    "charging.settings.targetStateOfChargeInPercent": "field_charging_settings_target_state_of_charge_in_percent",
    "charging.status.battery.remainingCruisingRangeInMeters": "field_charging_status_battery_remaining_cruising_range_in_meters",
    "charging.status.fullyChargedAt": "field_charging_status_fully_charged_at",
    "charging.status.chargePowerInKw": "field_charging_status_charge_power_in_kw",
    "charging.status.chargeType": "field_charging_status_charge_type",
    "charging.status.chargingRateInKilometersPerHour": "field_charging_status_charging_rate_in_kilometers_per_hour",
    "charging.status.plugConnectionState": "field_charging_status_plug_connection_state",
    "charging.status.remainingTimeToFullyChargedInMinutes": "field_charging_status_remaining_time_to_fully_charged_in_minutes",
    "airConditioning.targetTemperatureInCelsius": "field_air_conditioning_target_temperature_in_celsius",
    "airConditioning.settings.windowHeatingEnabled": "field_air_conditioning_settings_window_heating_enabled",
    "airConditioning.settings.climatisationAtUnlock": "field_air_conditioning_settings_climatisation_at_unlock",
    "vehicleStatus.overall.status": "field_vehicle_status_overall_status",
    "vehicleStatus.doors.frontLeft": "field_vehicle_status_doors_front_left",
    "vehicleStatus.doors.frontRight": "field_vehicle_status_doors_front_right",
    "vehicleStatus.doors.rearLeft": "field_vehicle_status_doors_rear_left",
    "vehicleStatus.doors.rearRight": "field_vehicle_status_doors_rear_right",
    "vehicleStatus.windows.frontLeft": "field_vehicle_status_windows_front_left",
    "vehicleStatus.windows.frontRight": "field_vehicle_status_windows_front_right",
    "vehicleStatus.windows.rearLeft": "field_vehicle_status_windows_rear_left",
    "vehicleStatus.windows.rearRight": "field_vehicle_status_windows_rear_right",
    "vehicleStatus.lights": "field_vehicle_status_lights",
    "vehicleStatus.odometerInKm": "field_vehicle_status_odometer_in_km"
})


# Additional observed API paths from real Home Assistant devices.
KNOWN_FIELD_KEYS.update({
    "airConditioning.airConditioningAtUnlock": "field_air_conditioning_air_conditioning_at_unlock",
    "airConditioning.windowHeating.enabled": "field_air_conditioning_window_heating_enabled",
    "airConditioning.windowHeating.front": "field_air_conditioning_window_heating_front",
    "airConditioning.windowHeating.rear": "field_air_conditioning_window_heating_rear",
    "charging.settings.autoUnlockPlugWhenCharged": "field_charging_settings_auto_unlock_plug_when_charged",
    "charging.status.plug.lockState": "field_charging_status_plug_lock_state",
    "charging.status.plugLockState": "field_charging_status_plug_lock_state",
    "charging.settings.availableChargeModes": "field_charging_settings_available_charge_modes",
    "charging.settings.availableChargeModes.0": "field_charging_settings_available_charge_modes_0",
    "charging.settings.availableChargeModes.1": "field_charging_settings_available_charge_modes_1",
    "charging.settings.availableChargeModes.2": "field_charging_settings_available_charge_modes_2",
    "charging.settings.availableChargeModes.3": "field_charging_settings_available_charge_modes_3",
    "charging.settings.batteryCareModeTargetStateOfChargeInPercent": "field_charging_settings_battery_care_mode_target_state_of_charge_in_percent",
    "charging.settings.maxChargeCurrentAc": "field_charging_settings_max_charge_current_ac",
    "charging.status.chargePowerInKW": "field_charging_status_charge_power_in_kw",
    "status.detail.bonnet": "field_status_detail_bonnet",
    "status.detail.trunk": "field_status_detail_trunk",
    "status.detail.sunroof": "field_status_detail_sunroof",
    "status.overall.doors": "field_status_overall_doors",
    "status.overall.doorsLocked": "field_status_overall_doors_locked",
    "status.overall.locked": "field_status_overall_locked",
    "status.overall.reliableLockStatus": "field_status_overall_reliable_lock_status",
    "status.overall.windows": "field_status_overall_windows",
    "status.overall.lights": "field_status_overall_lights",
    "licensePlate": "field_license_plate",
    "renderUrl": "field_render_url",
    "odometer.carCapturedTimestamp": "field_odometer_car_captured_timestamp",
    "odometer.mileageInKm": "field_odometer_mileage_in_km",
    "parking.position.address": "field_parking_position_address",
    "parking.position.gpsCoordinates.latitude": "field_parking_position_gps_coordinates_latitude",
    "parking.position.gpsCoordinates.longitude": "field_parking_position_gps_coordinates_longitude",
    "parking.position.state": "field_parking_position_state",
    "parking.position.gpsCoordinates": "field_parking_position_gps_coordinates",
    "chargingProfiles.carCapturedTimestamp": "field_charging_profiles_car_captured_timestamp",
    "chargingProfiles.currentVehiclePosition.latitude": "field_charging_profiles_current_vehicle_position_latitude",
    "chargingProfiles.currentVehiclePosition.longitude": "field_charging_profiles_current_vehicle_position_longitude",
    "chargingProfiles.currentVehiclePosition.address": "field_charging_profiles_current_vehicle_position_address",
    "chargingProfiles.currentVehiclePosition.state": "field_charging_profiles_current_vehicle_position_state",
    "chargingProfiles.profiles.0.id": "field_charging_profiles_profiles_0_id",
    "chargingProfiles.profiles.0.name": "field_charging_profiles_profiles_0_name",
    "chargingProfiles.profiles.0.preferredChargingTimes.0.enabled": "field_charging_profiles_profiles_0_preferred_charging_times_0_enabled",
    "chargingProfiles.profiles.0.preferredChargingTimes.0.startTime": "field_charging_profiles_profiles_0_preferred_charging_times_0_start_time",
    "chargingProfiles.profiles.0.preferredChargingTimes.0.endTime": "field_charging_profiles_profiles_0_preferred_charging_times_0_end_time",
    "chargingProfiles.profiles.0.settings.autoUnlockPlugWhenCharged": "field_charging_profiles_profiles_0_settings_auto_unlock_plug_when_charged",
    "chargingProfiles.profiles.0.settings.maxChargeCurrent": "field_charging_profiles_profiles_0_settings_max_charge_current",
    "chargingProfiles.profiles.0.settings.minBatteryStateOfChargeInPercent": "field_charging_profiles_profiles_0_settings_min_battery_state_of_charge_in_percent",
    "chargingProfiles.profiles.0.settings.targetStateOfChargeInPercent": "field_charging_profiles_profiles_0_settings_target_state_of_charge_in_percent",
    "chargingProfiles.profiles.0.settings.batteryCareMode": "field_charging_profiles_profiles_0_settings_battery_care_mode",
    "chargingProfiles.profiles.0.settings.preferredChargeMode": "field_charging_profiles_profiles_0_settings_preferred_charge_mode",
    "chargingProfiles.profiles.0.settings.chargingMode": "field_charging_profiles_profiles_0_settings_charging_mode"
})


def field_translation_key(path: str, available_keys: set[str]) -> str:
    """Use a static key only when its translation exists for the platform."""
    # Numeric array indices must not create new translation keys for each profile.
    canonical = re.sub(r"(?<=\.)\d+(?=\.|$)", "0", path)
    key = KNOWN_FIELD_KEYS.get(path) or KNOWN_FIELD_KEYS.get(canonical)
    return key if key in available_keys else "api_field"
