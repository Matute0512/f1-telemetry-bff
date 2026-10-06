from f1_telemetry_bff.domain.entities import Circuit


def test_circuit_creation() -> None:
    circuit = Circuit(
        circuit_key=6,
        name="Monza",
        country="Italy",
        location="Monza",
    )

    assert circuit.circuit_key == 6
    assert circuit.name == "Monza"
    assert circuit.country == "Italy"
    assert circuit.location == "Monza"
