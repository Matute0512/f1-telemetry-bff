from f1_telemetry_bff.config.settings import get_settings


def test_settings_have_default_values() -> None:
    settings = get_settings()

    assert settings.app_name == "F1 Telemetry BFF"
    assert settings.app_version == "0.1.0"
    assert settings.environment == "development"
    assert settings.openf1_base_url == "https://api.openf1.org/v1"
