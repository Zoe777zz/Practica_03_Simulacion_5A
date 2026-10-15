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
    service_times: List[float] = field(default_factory=list)
    completion_times: List[float] = field(default_factory=list)
    utilization_history: List[float] = field(default_factory=list)
    queue_times: List[float] = field(default_factory=list)
    queue_sizes: List[int] = field(default_factory=list)
    customers_completed: int = 0


class MM1Model:
    """Model: lógica de simulación, independiente de Flask y HTML."""

    def __init__(self, theory_strategy: TheoryStrategy):
        self.theory_strategy = theory_strategy

    def run(self, config: ScenarioConfig, seed: int) -> SimulationResult:
        theory = self.theory_strategy.calculate(config.arrival_rate, config.service_rate)
        rng = np.random.default_rng(seed)
        env = simpy.Environment()
        server = simpy.Resource(env, capacity=1)

        waiting_times: List[float] = []
        service_times: List[float] = []
        completion_times: List[float] = []
        utilization_history: List[float] = []
        queue_times: List[float] = []
        queue_sizes: List[int] = []

        total_busy_time = 0.0
        warmup = config.simulation_time * 0.10
        sample_interval = max(0.10, min(0.50, config.simulation_time / 3500))

        def customer():
            nonlocal total_busy_time
            arrival_time = env.now
            with server.request() as request:
                yield request
                start_service = env.now
                wait = start_service - arrival_time
                service_time = float(rng.exponential(1 / config.service_rate))
                yield env.timeout(service_time)
                departure_time = env.now
                total_busy_time += service_time
                rho_observed = total_busy_time / departure_time if departure_time > 0 else 0.0

                if departure_time >= warmup:
                    waiting_times.append(wait)
                    service_times.append(service_time)
                    completion_times.append(departure_time)
                    utilization_history.append(min(rho_observed, 1.0))

        def arrivals():
            while True:
                interarrival = float(rng.exponential(1 / config.arrival_rate))
                yield env.timeout(interarrival)
                if env.now > config.simulation_time:
                    break
                env.process(customer())

        def queue_monitor():
            while True:
                if env.now >= warmup:
                    queue_times.append(env.now)
                    queue_sizes.append(len(server.queue))
                yield env.timeout(sample_interval)

        env.process(arrivals())
        env.process(queue_monitor())
        env.run(until=config.simulation_time)

        return SimulationResult(
            theory=theory,
            average_wait_sim=float(np.mean(waiting_times)) if waiting_times else 0.0,
            average_queue_sim=float(np.mean(queue_sizes)) if queue_sizes else 0.0,
            waiting_times=waiting_times,
            service_times=service_times,
            completion_times=completion_times,
            utilization_history=utilization_history,
            queue_times=queue_times,
            queue_sizes=queue_sizes,
            customers_completed=len(waiting_times),
        )
