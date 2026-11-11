"""Standalone functional-group unit tests (no HA runtime needed)."""
from custom_components.skoda_public.groups import functional_group, binary_device_class


def test_grouping():
    assert functional_group("charging.status.state") == "charging"
    assert functional_group("battery.soc") == "battery"
    assert functional_group("parking.position.latitude") == "location"
    assert functional_group("airConditioning.state") == "climate"
    assert functional_group("fuel.level") == "engine"
    assert functional_group("vehicle.odometer") == "vehicle_info"


def test_binary_class():
    assert binary_device_class("status.doors.frontLeft.open") == "door"
    assert binary_device_class("status.windows.frontLeft.open") == "window"
    assert binary_device_class("status.lights.lowBeam") == "light"
