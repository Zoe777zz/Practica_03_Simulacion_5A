from src.patterns.scenario_factory import ScenarioConfig, ScenarioFactory


class SimulationController:
    """Controller de MVC: conecta la vista con el modelo."""

    def __init__(self, model, view, analyzer):
        self.model = model
        self.view = view
        self.analyzer = analyzer

    def load_scenario(self, scenario_name: str):
        try:
            config = ScenarioFactory.create(scenario_name)
            if config is None:
                self.view.enable_custom_inputs(True)
                return

            self.view.enable_custom_inputs(False)
            self.view.set_input_values(
                arrival_rate=config.arrival_rate,
                service_rate=config.service_rate,
                simulation_time=config.simulation_time,
                seed=config.seed,
            )
        except Exception as exc:
            self.view.show_error(str(exc))

    def run_simulation(self):
        try:
            values = self.view.get_input_values()

            config = ScenarioConfig(
                name=values["scenario"],
                arrival_rate=float(values["arrival_rate"]),
                service_rate=float(values["service_rate"]),
                simulation_time=float(values["simulation_time"]),
                seed=int(values["seed"]),
            )

            self.view.set_status("Ejecutando simulación...")
            self.view.update_idletasks()

            result = self.model.run(config)

            # ANALYZER: registra los resultados requeridos por la práctica.
            self.analyzer.register(config, result)

            self.view.show_result(result)
            self.view.show_comparison(self.analyzer.comparison_rows())
            self.view.set_status(
                f"Simulación finalizada. Resultados guardados en "
                f"{self.analyzer.csv_path}"
            )
        except ValueError as exc:
            self.view.show_error(str(exc))
            self.view.set_status("Corrige los datos e intenta nuevamente.")
        except Exception as exc:
            self.view.show_error(
                f"Ocurrió un error inesperado:\n{exc}"
            )
            self.view.set_status("Error durante la simulación.")

    def run_all_scenarios(self):
        try:
            self.view.set_status("Ejecutando los tres escenarios...")
            self.view.update_idletasks()

            last_result = None
            for name in ScenarioFactory.names():
                if name == "Personalizado":
                    continue

                config = ScenarioFactory.create(name)
                result = self.model.run(config)
                self.analyzer.register(config, result)
                last_result = result

            if last_result is not None:
                self.view.show_result(last_result)

            self.view.show_comparison(self.analyzer.comparison_rows())
            self.view.set_status(
                "Tres escenarios ejecutados y guardados en "
                f"{self.analyzer.csv_path}"
            )
        except Exception as exc:
            self.view.show_error(str(exc))
            self.view.set_status("Error durante la comparación.")

    def clear(self):
        self.view.clear_results()
        self.view.set_status("Listo.")
