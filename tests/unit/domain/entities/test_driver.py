from f1_telemetry_bff.domain.entities import Driver


def test_driver_creation() -> None:
    driver = Driver(
        driver_number=1,
        name="Max Verstappen",
        acronym="VER",
        team="Red Bull Racing",
    )

    assert driver.driver_number == 1
    assert driver.name == "Max Verstappen"
    assert driver.acronym == "VER"
    assert driver.team == "Red Bull Racing"
