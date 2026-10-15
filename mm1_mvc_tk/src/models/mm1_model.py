from dataclasses import dataclass, field
from typing import List

import numpy as np
import simpy

from src.patterns.scenario_factory import ScenarioConfig
from src.patterns.theory_strategy import TheoryMetrics, TheoryStrategy


@dataclass
class SimulationResult:
    theory: TheoryMetrics
    average_wait_sim: float
    average_queue_sim: float
    waiting_times: List[float] = field(default_factory=list)
    queue_times: List[float] = field(default_factory=list)
    queue_sizes: List[int] = field(default_factory=list)
    customers_completed: int = 0


class MM1Model:
    """Model de MVC: contiene la lógica del sistema M/M/1."""

    def __init__(self, theory_strategy: TheoryStrategy):
        self.theory_strategy = theory_strategy

    def run(self, config: ScenarioConfig) -> SimulationResult:
        self._validate(config)

        theory = self.theory_strategy.calculate(
            config.arrival_rate,
            config.service_rate,
        )

        rng = np.random.default_rng(config.seed)
        env = simpy.Environment()
        server = simpy.Resource(env, capacity=1)

        waiting_times = []
        queue_times = []
        queue_sizes = []

        # Se descarta un pequeño periodo inicial para reducir el sesgo
        # del sistema vacío al comienzo de la simulación.
        warmup = config.simulation_time * 0.10
        sample_interval = max(0.05, min(0.25, config.simulation_time / 5000))

        def customer(customer_id: int):
            arrival_time = env.now

            with server.request() as request:
                yield request

                wait = env.now - arrival_time
                if env.now >= warmup:
                    waiting_times.append(wait)

                service_time = rng.exponential(1 / config.service_rate)
                yield env.timeout(service_time)

        def arrivals():
            customer_id = 0
            while True:
                interarrival = rng.exponential(1 / config.arrival_rate)
                yield env.timeout(interarrival)

                if env.now > config.simulation_time:
                    break

                customer_id += 1
                env.process(customer(customer_id))

        def queue_monitor():
            while True:
                if env.now >= warmup:
                    queue_times.append(env.now)
                    queue_sizes.append(len(server.queue))
                yield env.timeout(sample_interval)

        env.process(arrivals())
        env.process(queue_monitor())
        env.run(until=config.simulation_time)

        average_wait = float(np.mean(waiting_times)) if waiting_times else 0.0
        average_queue = float(np.mean(queue_sizes)) if queue_sizes else 0.0

        return SimulationResult(
            theory=theory,
            average_wait_sim=average_wait,
            average_queue_sim=average_queue,
            waiting_times=waiting_times,
            queue_times=queue_times,
            queue_sizes=queue_sizes,
            customers_completed=len(waiting_times),
        )

    @staticmethod
    def _validate(config: ScenarioConfig):
        if config.arrival_rate <= 0:
            raise ValueError("λ debe ser mayor que cero.")
        if config.service_rate <= 0:
            raise ValueError("μ debe ser mayor que cero.")
        if config.arrival_rate >= config.service_rate:
            raise ValueError(
                "Sistema inestable: debe cumplirse λ < μ."
            )
        if config.simulation_time <= 0:
            raise ValueError("El tiempo de simulación debe ser mayor que cero.")
