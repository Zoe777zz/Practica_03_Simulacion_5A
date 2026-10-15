from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List


@dataclass
class ScenarioRecord:
    scenario: str
    arrival_rate: float
    service_rate: float
    rho: float
    L: float
    Lq: float
    W: float
    Wq: float
    average_wait_sim: float
    average_queue_sim: float


class ResultAnalyzer:
    """
    Analyzer del proyecto.

    Responsabilidades:
    - registrar los resultados obtenidos en cada escenario;
    - conservar los datos requeridos por la práctica;
    - generar una tabla comparativa;
    - guardar los resultados en CSV para usarlos en el informe.
    """

    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.output_dir / "resultados_escenarios.csv"
        self.records: List[ScenarioRecord] = []
        self._load_existing()

    def _load_existing(self):
        if not self.csv_path.exists():
            return

        try:
            with self.csv_path.open("r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.records.append(
                        ScenarioRecord(
                            scenario=row["scenario"],
                            arrival_rate=float(row["arrival_rate"]),
                            service_rate=float(row["service_rate"]),
                            rho=float(row["rho"]),
                            L=float(row["L"]),
                            Lq=float(row["Lq"]),
                            W=float(row["W"]),
                            Wq=float(row["Wq"]),
                            average_wait_sim=float(row["average_wait_sim"]),
                            average_queue_sim=float(row["average_queue_sim"]),
                        )
                    )
        except (OSError, ValueError, KeyError):
            # Si el archivo fue editado manualmente y quedó inválido,
            # se inicia una colección limpia.
            self.records = []

    def register(self, config, result):
        record = ScenarioRecord(
            scenario=config.name,
            arrival_rate=config.arrival_rate,
            service_rate=config.service_rate,
            rho=result.theory.rho,
            L=result.theory.L,
            Lq=result.theory.Lq,
            W=result.theory.W,
            Wq=result.theory.Wq,
            average_wait_sim=result.average_wait_sim,
            average_queue_sim=result.average_queue_sim,
        )

        # Para escenarios oficiales se conserva solo el resultado más reciente,
        # evitando filas duplicadas al ejecutar varias veces.
        self.records = [
            item for item in self.records
            if item.scenario != config.name
        ]
        self.records.append(record)
        self._save()
        return record

    def get_records(self):
        order = {
            "Escenario 1 - Estable": 1,
            "Escenario 2 - Mayor utilización": 2,
            "Escenario 3 - Cerca de saturación": 3,
        }
        return sorted(
            self.records,
            key=lambda item: (order.get(item.scenario, 99), item.scenario),
        )

    def comparison_rows(self):
        """
        Retorna exactamente los datos pedidos en la guía:
        ρ, L, Lq, W, Wq, tiempo promedio de espera simulado
        y tamaño promedio de cola simulado.
        """
        rows = []
        for item in self.get_records():
            rows.append(
                {
                    "Escenario": item.scenario,
                    "λ": item.arrival_rate,
                    "μ": item.service_rate,
                    "ρ": item.rho,
                    "L": item.L,
                    "Lq": item.Lq,
                    "W": item.W,
                    "Wq": item.Wq,
                    "Espera simulada": item.average_wait_sim,
                    "Cola promedio simulada": item.average_queue_sim,
                }
            )
        return rows

    def _save(self):
        fieldnames = [
            "scenario",
            "arrival_rate",
            "service_rate",
            "rho",
            "L",
            "Lq",
            "W",
            "Wq",
            "average_wait_sim",
            "average_queue_sim",
        ]

        with self.csv_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for item in self.get_records():
                writer.writerow(asdict(item))
