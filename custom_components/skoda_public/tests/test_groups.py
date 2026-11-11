"""Standalone unit tests for grouping without importing Home Assistant."""
import importlib.util
from pathlib import Path

module_path = Path(__file__).resolve().parents[1] / "groups.py"
spec = importlib.util.spec_from_file_location("skoda_groups", module_path)
groups = importlib.util.module_from_spec(spec)
spec.loader.exec_module(groups)


def test_grouping():
    assert groups.functional_group("charging.status.state") == "charging"
    assert groups.functional_group("battery.soc") == "battery"
    assert groups.functional_group("parking.position.latitude") == "location"
    assert groups.functional_group("airConditioning.state") == "climate"
    assert groups.functional_group("fuel.level") == "engine"
    assert groups.functional_group("vehicle.odometer") == "vehicle_info"


def test_binary_class():
    assert groups.binary_device_class("status.doors.frontLeft.open") == "door"
    assert groups.binary_device_class("status.windows.frontLeft.open") == "window"
    assert groups.binary_device_class("status.lights.lowBeam") == "light"
