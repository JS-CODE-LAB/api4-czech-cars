"""Security helpers can be tested without a Home Assistant installation."""
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "custom_components" / "skoda_public" / "security.py"
spec = importlib.util.spec_from_file_location("skoda_security", path)
security = importlib.util.module_from_spec(spec)
spec.loader.exec_module(security)


def test_redacts_credentials_and_vin():
    message = "API key secret-123 for VIN ABCDEFGHIJKLMNOPQ rejected; S-PIN 1234"
    actual = security.redact_sensitive(message, "secret-123", "ABCDEFGHIJKLMNOPQ", "1234")
    assert "secret-123" not in actual
    assert "ABCDEFGHIJKLMNOPQ" not in actual
    assert "1234" not in actual
    assert actual.count("[REDACTED]") == 3


def test_ignores_empty_and_short_secrets():
    assert security.redact_sensitive("HTTP 429", None, "", "42") == "HTTP 429"
