from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioConfig:
    key: str
    name: str
    arrival_rate: float
    service_rate: float
    condition: str
    simulation_time: float = 1000.0


class ScenarioFactory:
    """Factory de los tres escenarios fijos indicados por la práctica."""

    _SCENARIOS = (
        ScenarioConfig(
            key="scenario_1",
            name="Escenario 1",
            arrival_rate=2.0,
            service_rate=3.0,
            condition="Sistema estable",
        ),
        ScenarioConfig(
            key="scenario_2",
            name="Escenario 2",
            arrival_rate=2.5,
            service_rate=3.0,
            condition="Mayor utilización",
        ),
        ScenarioConfig(
            key="scenario_3",
            name="Escenario 3",
            arrival_rate=2.9,
            service_rate=3.0,
            condition="Cerca de saturación",
        ),
    )

    @classmethod
    def all(cls):
        return list(cls._SCENARIOS)

    @classmethod
    def by_key(cls, key: str) -> ScenarioConfig:
        for scenario in cls._SCENARIOS:
            if scenario.key == key:
                return scenario
        raise ValueError(f"Escenario desconocido: {key}")
