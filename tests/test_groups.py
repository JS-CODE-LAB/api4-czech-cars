"""Standalone unit tests for grouping without importing Home Assistant."""
import importlib.util
from pathlib import Path

module_path = Path(__file__).resolve().parents[1] / "custom_components" / "skoda_public" / "groups.py"
spec = importlib.util.spec_from_file_location("skoda_groups", module_path)
groups = importlib.util.module_from_spec(spec)
spec.loader.exec_module(groups)


def test_grouping():
    assert groups.functional_group("charging.status.state") == "charging"
    assert groups.functional_group("battery.soc") == "battery"
    assert groups.functional_group("parking.position.latitude") == "location"
    assert groups.functional_group("airConditioning.state") == "climate"
    assert groups.functional_group("fuel.level") == "powertrain"
    assert groups.functional_group("vehicle.odometer") == "counters"


def test_subgroups():
    assert groups.functional_group("chargingProfiles.0.name") == "charging_profiles"
    assert groups.functional_group("vehicle.doors.frontLeft") == "doors"
    assert groups.functional_group("vehicle.windows.frontLeft") == "windows"
    assert groups.functional_group("vehicle.lights.lowBeam") == "lights"
    assert groups.functional_group("vehicle.tripMeter") == "counters"
    assert groups.functional_group("vehicle.settings.mode") == "settings"
    assert set(groups.GROUPS) == set(groups.GROUP_NAMES)


def test_binary_class():
    assert groups.binary_device_class("status.doors.frontLeft.open") == "door"
    assert groups.binary_device_class("status.windows.frontLeft.open") == "window"
    assert groups.binary_device_class("status.lights.lowBeam") == "light"
