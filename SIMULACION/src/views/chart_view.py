import base64
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class ChartView:
    """Genera una figura PNG en memoria; no persiste resultados en disco."""

    @staticmethod
    def render(result, scenario_name: str) -> str:
        fig = plt.figure(figsize=(11, 7.2), dpi=120)
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.15], hspace=0.38, wspace=0.25)
        ax_queue = fig.add_subplot(gs[0, 0])
        ax_wait = fig.add_subplot(gs[0, 1])
        ax_relation = fig.add_subplot(gs[1, :])

        if result.queue_times:
            step = max(1, len(result.queue_times) // 1600)
            ax_queue.plot(
                result.queue_times[::step],
                result.queue_sizes[::step],
                linewidth=1.2,
                color="#2563eb",
            )
        ax_queue.set_title("Comportamiento de la cola")
        ax_queue.set_xlabel("Tiempo de simulación")
        ax_queue.set_ylabel("Clientes en cola")
        ax_queue.grid(alpha=0.18)

        if result.completion_times:
            ax_wait.plot(
                result.completion_times,
                result.waiting_times,
                linewidth=0.8,
                color="#0ea5e9",
            )
        ax_wait.set_title("Tiempo de espera")
        ax_wait.set_xlabel("Tiempo de simulación")
        ax_wait.set_ylabel("Tiempo de espera")
        ax_wait.grid(alpha=0.18)

        if result.completion_times:
            ax_relation.plot(
                result.completion_times,
                result.waiting_times,
                label="Tiempo de espera",
                linewidth=0.8,
                color="#0284c7",
            )
            ax_relation.plot(
                result.completion_times,
                result.service_times,
                label="Tiempo de ejecución/servicio",
                linewidth=0.8,
                color="#7c3aed",
            )

            rho_axis = ax_relation.twinx()
            rho_axis.plot(
                result.completion_times,
                result.utilization_history,
                label="ρ observado",
                linewidth=1.15,
                color="#14b8a6",
            )
            rho_axis.axhline(
                result.theory.rho,
                linestyle="--",
                linewidth=1.2,
                label="ρ teórico",
                color="#f59e0b",
            )
            rho_axis.set_ylabel("ρ")
            rho_axis.set_ylim(0, 1.05)

            l1, t1 = ax_relation.get_legend_handles_labels()
            l2, t2 = rho_axis.get_legend_handles_labels()
            ax_relation.legend(l1 + l2, t1 + t2, loc="upper left", ncol=2, fontsize=8)

        ax_relation.set_title("ρ, espera y tiempo de ejecución a través del tiempo")
        ax_relation.set_xlabel("Tiempo de simulación")
        ax_relation.set_ylabel("Tiempo")
        ax_relation.grid(alpha=0.18)

        fig.suptitle(f"{scenario_name} — última repetición", fontsize=15, fontweight="bold", color="#0f2f63")
        fig.patch.set_facecolor("#f8fbff")
        for ax in [ax_queue, ax_wait, ax_relation]:
            ax.set_facecolor("#ffffff")
            for spine in ax.spines.values():
                spine.set_alpha(0.15)

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        buffer.seek(0)
        return "data:image/png;base64," + base64.b64encode(buffer.read()).decode("ascii")
