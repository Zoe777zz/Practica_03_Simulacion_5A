import secrets

from src.patterns.scenario_factory import ScenarioFactory


class SimulationController:
    """Controller: coordina N repeticiones, semilla común, análisis y vista."""

    def __init__(self, model, analyzer, chart_view):
        self.model = model
        self.analyzer = analyzer
        self.chart_view = chart_view

    def run_experiment(self, repetitions: int):
        if repetitions < 1:
            raise ValueError("N debe ser al menos 1.")
        if repetitions > 50:
            raise ValueError("Para mantener una respuesta fluida, N debe ser máximo 50.")

        scenarios = ScenarioFactory.all()
        results = {s.key: [] for s in scenarios}
        seeds = []

        for _ in range(repetitions):
            shared_seed = secrets.randbits(32)
            seeds.append(shared_seed)
            for scenario in scenarios:
                results[scenario.key].append(self.model.run(scenario, shared_seed))

        summaries = []
        details = {}
        for scenario in scenarios:
            scenario_results = results[scenario.key]
            summaries.append(self.analyzer.summarize(scenario, scenario_results))
            last = scenario_results[-1]
            details[scenario.key] = {
                "key": scenario.key,
                "scenario": scenario.name,
                "lambda": scenario.arrival_rate,
                "mu": scenario.service_rate,
                "condition": scenario.condition,
                "rho": last.theory.rho,
                "chart_image": self.chart_view.render(last, scenario.name),
            }

        seed_message = (
            f"Semilla automática compartida: {seeds[0]}"
            if repetitions == 1
            else f"Se generaron {repetitions} semillas automáticas; en cada repetición la misma semilla se utilizó para los 3 escenarios."
        )

        return {
            "repetitions": repetitions,
            "seed_message": seed_message,
            "summaries": summaries,
            "details": details,
        }
