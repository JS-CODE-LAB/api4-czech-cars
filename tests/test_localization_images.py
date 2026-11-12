"""Standalone checks for Czech names and image-field detection."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "skoda_public"


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


loc = load("localization")
img = load("image_fields")


def test_czech_labels():
    assert loc.localized_path("charging.status.stateOfChargeInPercent", "cs").startswith("Nabíjení stav")
    assert "stav nabití" in loc.localized_path("charging.status.stateOfChargeInPercent", "cs")
    assert "přední levé" in loc.localized_path("vehicle.doors.frontLeft.open", "cs-CZ")
    assert loc.localized_path("charging.status.state", "en") == "Charging status state"


def test_images():
    assert img.is_image_field("vehicle.imageUrl", "https://example.com/a")
    assert img.is_image_field("vehicle.unknown", "https://example.com/car.png?size=1")
    assert not img.is_image_field("vehicle.imageUrl", "http://example.com/car.png")
    assert not img.is_image_field("vehicle.imageUrl", "hello")
    assert not img.is_image_field("vehicle.website", "https://example.com")

def test_reported_czech_labels():
    assert loc.localized_path("licensePlate", "cs") == "Registrační značka"
    assert loc.localized_path("operations.0.name", "cs") == "Operace 1 – název"
    assert loc.localized_path("renderUrl", "cs") == "Obrázek vozidla"
    assert loc.localized_path("status.carCaptured.timestamp", "cs") == "Čas pořízení údajů o vozidle"
