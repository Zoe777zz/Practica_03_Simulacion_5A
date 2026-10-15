from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioConfig:
    name: str
    arrival_rate: float
    service_rate: float
    simulation_time: float = 1000.0
    seed: int = 42


class ScenarioFactory:
    """Factory: crea configuraciones de escenarios del experimento."""

    _SCENARIOS = {
        "Escenario 1 - Estable": ScenarioConfig(
            name="Escenario 1 - Estable",
            arrival_rate=2.0,
            service_rate=3.0,
        ),
        "Escenario 2 - Mayor utilización": ScenarioConfig(
            name="Escenario 2 - Mayor utilización",
            arrival_rate=2.5,
            service_rate=3.0,
        ),
        "Escenario 3 - Cerca de saturación": ScenarioConfig(
            name="Escenario 3 - Cerca de saturación",
            arrival_rate=2.9,
            service_rate=3.0,
        ),
    }

    @classmethod
    def names(cls):
        return list(cls._SCENARIOS.keys()) + ["Personalizado"]

    @classmethod
    def create(cls, name: str) -> ScenarioConfig | None:
        if name == "Personalizado":
            return None
        scenario = cls._SCENARIOS.get(name)
        if scenario is None:
            raise ValueError(f"Escenario desconocido: {name}")
        return scenario
