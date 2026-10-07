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
    assert driver.team_name == "Red Bull Racing"
    assert driver.team_colour is None


def test_driver_creation_with_team_name_and_colour() -> None:
    driver = Driver(
        driver_number=44,
        name="Lewis Hamilton",
        acronym="HAM",
        team_name="Mercedes",
        team_colour="00D2BE",
    )

    assert driver.driver_number == 44
    assert driver.name == "Lewis Hamilton"
    assert driver.acronym == "HAM"
    assert driver.team == "Mercedes"
    assert driver.team_name == "Mercedes"
    assert driver.team_colour == "00D2BE"
