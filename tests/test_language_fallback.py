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
