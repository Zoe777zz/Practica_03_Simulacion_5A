from src.analyzers.result_analyzer import ResultAnalyzer
from src.controllers.simulation_controller import SimulationController
from src.models.mm1_model import MM1Model
from src.patterns.theory_strategy import MM1TheoryStrategy
from src.views.main_view import MainView


def main():
    model = MM1Model(theory_strategy=MM1TheoryStrategy())
    analyzer = ResultAnalyzer()
    view = MainView()
    controller = SimulationController(
        model=model,
        view=view,
        analyzer=analyzer,
    )
    view.set_controller(controller)
    view.show_comparison(analyzer.comparison_rows())
    view.mainloop()


if __name__ == "__main__":
    main()
