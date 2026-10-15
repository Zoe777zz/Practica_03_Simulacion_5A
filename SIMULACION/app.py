from flask import Flask, jsonify, render_template, request

from src.analyzers.result_analyzer import ResultAnalyzer
from src.controllers.simulation_controller import SimulationController
from src.models.mm1_model import MM1Model
from src.patterns.scenario_factory import ScenarioFactory
from src.patterns.theory_strategy import MM1TheoryStrategy
from src.views.chart_view import ChartView


app = Flask(__name__)

controller = SimulationController(
    model=MM1Model(theory_strategy=MM1TheoryStrategy()),
    analyzer=ResultAnalyzer(),
    chart_view=ChartView(),
)


@app.get("/")
def index():
    return render_template("index.html", scenarios=ScenarioFactory.all())


@app.post("/api/simulate")
def simulate():
    try:
        payload = request.get_json(silent=True) or {}
        repetitions = int(payload.get("repetitions", 1))
        return jsonify({"ok": True, "data": controller.run_experiment(repetitions)})
    except (TypeError, ValueError) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"ok": False, "error": f"Error inesperado: {exc}"}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
