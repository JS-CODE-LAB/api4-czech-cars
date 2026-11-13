"""Locale fallback tests; no Home Assistant installation required."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "skoda_public"


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


groups = load_module("groups")
localization = load_module("localization")


def test_all_groups_have_english_names():
    assert set(groups.GROUP_NAMES) == set(groups.GROUP_NAMES_EN)


def test_group_names_by_locale():
    for locale in ("cs", "cs-CZ", "cs_CZ"):
        assert groups.group_name("charging", locale) == "Nabíjení"
    for locale in ("en", "en-US", "de", "sk", "fr", "", None):
        assert groups.group_name("charging", locale) == "Charging"
    assert groups.group_name("unknown_group", "de") == "unknown_group"


def test_dynamic_entity_labels_by_locale():
    path = "charging.status.battery.stateOfChargeInPercent"
    assert localization.localized_path(path, "cs") != localization.humanize_path(path)
    assert localization.localized_path(path, "cs-CZ") != localization.humanize_path(path)
    for locale in ("en", "de", "sk", "fr", ""):
        assert localization.localized_path(path, locale) == localization.humanize_path(path)

def test_translation_templates_use_per_user_language():
    import json
    for locale, field in (("cs", "field_cs"), ("en", "field_en")):
        translation = json.loads((ROOT / "translations" / f"{locale}.json").read_text())
        for platform, key in (
            ("sensor", "api_field"),
            ("binary_sensor", "api_field"),
            ("image", "original_api_field"),
            ("device_tracker", "api_field"),
        ):
            assert translation["entity"][platform][key]["name"] == "{" + field + "}"
    strings = json.loads((ROOT / "strings.json").read_text())
    assert strings["entity"]["sensor"]["api_field"]["name"] == "{field_en}"


def test_known_field_translations_present_in_all_locales():
    import json
    for locale in ("cs", "en"):
        translations = json.loads((ROOT / "translations" / f"{locale}.json").read_text())
        for platform in ("sensor", "binary_sensor", "image", "device_tracker"):
            keys = set(translations["entity"][platform])
            assert set(localization.KNOWN_FIELD_KEYS.values()) <= keys
    assert localization.field_translation_key(
        "airConditioning.state", set(localization.KNOWN_FIELD_KEYS.values())
    ) == "air_conditioning_state"
    assert localization.field_translation_key(
        "unknown.path", set(localization.KNOWN_FIELD_KEYS.values())
    ) == "api_field"


def test_expanded_field_translation_coverage():
    import json
    assert len(localization.KNOWN_FIELD_KEYS) >= 30
    for locale in ("cs", "en"):
        data = json.loads((ROOT / "translations" / f"{locale}.json").read_text())
        for platform in ("sensor", "binary_sensor", "image", "device_tracker"):
            assert set(localization.KNOWN_FIELD_KEYS.values()) <= set(data["entity"][platform])
    assert localization.field_translation_key(
        "charging.settings.targetStateOfChargeInPercent",
        set(localization.KNOWN_FIELD_KEYS.values())
    ) != "api_field"


def test_observed_paths_and_indexed_profiles():
    import json
    keys = set(localization.KNOWN_FIELD_KEYS.values())
    examples = (
        "status.detail.bonnet",
        "status.overall.windows",
        "licensePlate",
        "odometer.mileageInKm",
        "parking.position.state",
        "charging.settings.autoUnlockPlugWhenCharged",
        "chargingProfiles.profiles.3.settings.maxChargeCurrent",
        "chargingProfiles.profiles.2.preferredChargingTimes.4.startTime",
    )
    for path in examples:
        assert localization.field_translation_key(path, keys) != "api_field", path
    assert localization.profile_number("chargingProfiles.profiles.3.name") == "4"
    assert localization.profile_number("charging.status.state") == "1"
    for locale in ("cs", "en"):
        data = json.loads((ROOT / "translations" / f"{locale}.json").read_text())
        for platform in ("sensor", "binary_sensor", "image", "device_tracker"):
            assert keys <= set(data["entity"][platform])
            assert "{profile}" in data["entity"][platform][
                "field_charging_profiles_profiles_0_settings_max_charge_current"
            ]["name"]


def test_timer_translation_indices_and_placeholders():
    import json
    keys = set(localization.KNOWN_FIELD_KEYS.values())
    cases = (
        ("chargingProfiles.profiles.0.timers.0.id", "profile_timer_id"),
        ("chargingProfiles.profiles.2.timers.3.time", "profile_timer_time"),
        ("chargingProfiles.profiles.0.timers.1.recurrenceDays.4", "profile_timer_recurrence_day"),
        ("chargingProfiles.profiles.3.preferredChargingTimes.2.startTime",
         "field_charging_profiles_profiles_0_preferred_charging_times_0_start_time"),
    )
    for path, expected in cases:
        assert localization.field_translation_key(path, keys) == expected
    assert localization.profile_number("chargingProfiles.profiles.2.timers.1.id") == "3"
    assert localization.timer_number("chargingProfiles.profiles.2.timers.1.id") == "2"
    assert localization.day_number("chargingProfiles.profiles.2.timers.1.recurrenceDays.4") == "5"
    for locale in ("cs", "en"):
        data = json.loads((ROOT / "translations" / f"{locale}.json").read_text())
        for platform in ("sensor", "binary_sensor", "image", "device_tracker"):
            assert keys <= set(data["entity"][platform])
            assert "{timer}" in data["entity"][platform]["profile_timer_id"]["name"]
