import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.patterns.scenario_factory import ScenarioFactory


class MainView(tk.Tk):
    """View de MVC: interfaz local construida con Tkinter."""

    def __init__(self):
        super().__init__()
        self.controller = None

        self.title("Simulador M/M/1 - SimPy")
        self.geometry("1280x820")
        self.minsize(1120, 720)

        self._configure_style()
        self._build_layout()

    def set_controller(self, controller):
        self.controller = controller
        self.scenario_combo.bind("<<ComboboxSelected>>", self._on_scenario_change)
        self.run_button.config(command=self.controller.run_simulation)
        self.run_all_button.config(command=self.controller.run_all_scenarios)
        self.clear_button.config(command=self.controller.clear)
        self.scenario_combo.current(0)
        self._on_scenario_change()

    def _configure_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Title.TLabel", font=("TkDefaultFont", 17, "bold"))
        style.configure("Section.TLabelframe.Label", font=("TkDefaultFont", 11, "bold"))
        style.configure("Metric.Treeview", rowheight=27)
        style.configure("Accent.TButton", font=("TkDefaultFont", 10, "bold"))

    def _build_layout(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(18, 14))
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(
            header,
            text="Simulación de un sistema de líneas de espera M/M/1",
            style="Title.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="MVC · SimPy · Tkinter · Analyzer · Factory · Strategy",
        ).pack(anchor="w", pady=(3, 0))

        left = ttk.Frame(self, padding=(18, 4, 10, 12))
        left.grid(row=1, column=0, sticky="nsw")

        right = ttk.Frame(self, padding=(10, 4, 18, 12))
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=3)
        right.rowconfigure(1, weight=2)

        self._build_inputs(left)
        self._build_metrics(left)
        self._build_charts(right)
        self._build_comparison(right)

        status_frame = ttk.Frame(self, padding=(18, 6))
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.status_var = tk.StringVar(value="Listo.")
        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor="w")

    def _build_inputs(self, parent):
        box = ttk.LabelFrame(
            parent,
            text="Parámetros de simulación",
            style="Section.TLabelframe",
            padding=12,
        )
        box.pack(fill="x", pady=(0, 12))

        ttk.Label(box, text="Escenario:").grid(row=0, column=0, sticky="w", pady=5)
        self.scenario_var = tk.StringVar()
        self.scenario_combo = ttk.Combobox(
            box,
            textvariable=self.scenario_var,
            values=ScenarioFactory.names(),
            state="readonly",
            width=31,
        )
        self.scenario_combo.grid(row=0, column=1, sticky="ew", pady=5)

        self.arrival_var = tk.StringVar(value="2.0")
        self.service_var = tk.StringVar(value="3.0")
        self.time_var = tk.StringVar(value="1000")
        self.seed_var = tk.StringVar(value="42")

        self.entries = {}

        fields = [
            ("λ - Tasa de llegada:", self.arrival_var, "arrival"),
            ("μ - Tasa de servicio:", self.service_var, "service"),
            ("Tiempo de simulación:", self.time_var, "time"),
            ("Semilla aleatoria:", self.seed_var, "seed"),
        ]

        for row, (label, var, key) in enumerate(fields, start=1):
            ttk.Label(box, text=label).grid(row=row, column=0, sticky="w", pady=5)
            entry = ttk.Entry(box, textvariable=var, width=20)
            entry.grid(row=row, column=1, sticky="ew", pady=5)
            self.entries[key] = entry

        self.run_button = ttk.Button(
            box,
            text="Ejecutar escenario",
            style="Accent.TButton",
        )
        self.run_button.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 5))

        self.run_all_button = ttk.Button(
            box,
            text="Ejecutar y comparar los 3 escenarios",
        )
        self.run_all_button.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)

        self.clear_button = ttk.Button(box, text="Limpiar vista")
        self.clear_button.grid(row=7, column=0, columnspan=2, sticky="ew", pady=5)

    def _build_metrics(self, parent):
        box = ttk.LabelFrame(
            parent,
            text="Resultado del escenario actual",
            style="Section.TLabelframe",
            padding=10,
        )
        box.pack(fill="both", expand=True)

        self.metrics_tree = ttk.Treeview(
            box,
            columns=("metric", "value"),
            show="headings",
            height=10,
            style="Metric.Treeview",
        )
        self.metrics_tree.heading("metric", text="Métrica")
        self.metrics_tree.heading("value", text="Valor")
        self.metrics_tree.column("metric", width=195, anchor="w")
        self.metrics_tree.column("value", width=125, anchor="center")
        self.metrics_tree.pack(fill="both", expand=True)

    def _build_charts(self, parent):
        box = ttk.LabelFrame(
            parent,
            text="Visualización",
            style="Section.TLabelframe",
            padding=8,
        )
        box.grid(row=0, column=0, sticky="nsew", pady=(0, 8))

        self.figure = Figure(figsize=(7.7, 4.6), dpi=100)
        self.ax_queue = self.figure.add_subplot(121)
        self.ax_wait = self.figure.add_subplot(122)

        self.ax_queue.set_title("Tamaño de cola")
        self.ax_queue.set_xlabel("Tiempo")
        self.ax_queue.set_ylabel("Clientes")

        self.ax_wait.set_title("Tiempos de espera")
        self.ax_wait.set_xlabel("Cliente")
        self.ax_wait.set_ylabel("Tiempo")

        self.figure.tight_layout(pad=2.0)

        self.canvas = FigureCanvasTkAgg(self.figure, master=box)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _build_comparison(self, parent):
        box = ttk.LabelFrame(
            parent,
            text="Analyzer - Comparación de resultados",
            style="Section.TLabelframe",
            padding=8,
        )
        box.grid(row=1, column=0, sticky="nsew")

        columns = (
            "scenario", "rho", "L", "Lq", "W", "Wq",
            "wait_sim", "queue_sim"
        )
        self.comparison_tree = ttk.Treeview(
            box,
            columns=columns,
            show="headings",
            height=7,
        )

        headings = {
            "scenario": "Escenario",
            "rho": "ρ",
            "L": "L",
            "Lq": "Lq",
            "W": "W",
            "Wq": "Wq",
            "wait_sim": "Espera sim.",
            "queue_sim": "Cola sim.",
        }

        for column in columns:
            self.comparison_tree.heading(column, text=headings[column])

        self.comparison_tree.column("scenario", width=220, anchor="w")
        for column in columns[1:]:
            self.comparison_tree.column(column, width=85, anchor="center")

        xscroll = ttk.Scrollbar(
            box,
            orient="horizontal",
            command=self.comparison_tree.xview,
        )
        self.comparison_tree.configure(xscrollcommand=xscroll.set)

        self.comparison_tree.pack(fill="both", expand=True)
        xscroll.pack(fill="x")

    def _on_scenario_change(self, _event=None):
        if self.controller:
            self.controller.load_scenario(self.scenario_var.get())

    def get_input_values(self):
        return {
            "scenario": self.scenario_var.get(),
            "arrival_rate": self.arrival_var.get().strip(),
            "service_rate": self.service_var.get().strip(),
            "simulation_time": self.time_var.get().strip(),
            "seed": self.seed_var.get().strip(),
        }

    def set_input_values(self, arrival_rate, service_rate, simulation_time, seed):
        self.arrival_var.set(str(arrival_rate))
        self.service_var.set(str(service_rate))
        self.time_var.set(str(simulation_time))
        self.seed_var.set(str(seed))

    def enable_custom_inputs(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.entries["arrival"].config(state=state)
        self.entries["service"].config(state=state)
        self.entries["time"].config(state="normal")
        self.entries["seed"].config(state="normal")

    def show_result(self, result):
        for item in self.metrics_tree.get_children():
            self.metrics_tree.delete(item)

        metrics = [
            ("ρ - Utilización teórica", result.theory.rho),
            ("L - Clientes en sistema", result.theory.L),
            ("Lq - Clientes en cola", result.theory.Lq),
            ("W - Tiempo en sistema", result.theory.W),
            ("Wq - Espera teórica", result.theory.Wq),
            ("Espera promedio simulada", result.average_wait_sim),
            ("Cola promedio simulada", result.average_queue_sim),
            ("Clientes analizados", result.customers_completed),
        ]

        for name, value in metrics:
            shown = f"{value:.4f}" if isinstance(value, float) else str(value)
            self.metrics_tree.insert("", "end", values=(name, shown))

        self._plot_result(result)

    def show_comparison(self, rows):
        for item in self.comparison_tree.get_children():
            self.comparison_tree.delete(item)

        for row in rows:
            self.comparison_tree.insert(
                "",
                "end",
                values=(
                    row["Escenario"],
                    f'{row["ρ"]:.4f}',
                    f'{row["L"]:.4f}',
                    f'{row["Lq"]:.4f}',
                    f'{row["W"]:.4f}',
                    f'{row["Wq"]:.4f}',
                    f'{row["Espera simulada"]:.4f}',
                    f'{row["Cola promedio simulada"]:.4f}',
                ),
            )

    def _plot_result(self, result):
        self.ax_queue.clear()
        self.ax_wait.clear()

        self.ax_queue.set_title("Tamaño de cola")
        self.ax_queue.set_xlabel("Tiempo")
        self.ax_queue.set_ylabel("Clientes")

        if result.queue_times:
            step = max(1, len(result.queue_times) // 2500)
            self.ax_queue.plot(
                result.queue_times[::step],
                result.queue_sizes[::step],
                linewidth=1,
            )

        self.ax_wait.set_title("Tiempos de espera")
        self.ax_wait.set_xlabel("Cliente")
        self.ax_wait.set_ylabel("Tiempo")

        if result.waiting_times:
            self.ax_wait.plot(
                range(1, len(result.waiting_times) + 1),
                result.waiting_times,
                linewidth=0.9,
            )

        self.figure.tight_layout(pad=2.0)
        self.canvas.draw_idle()

    def clear_results(self):
        for item in self.metrics_tree.get_children():
            self.metrics_tree.delete(item)

        self.ax_queue.clear()
        self.ax_wait.clear()
        self.ax_queue.set_title("Tamaño de cola")
        self.ax_queue.set_xlabel("Tiempo")
        self.ax_queue.set_ylabel("Clientes")
        self.ax_wait.set_title("Tiempos de espera")
        self.ax_wait.set_xlabel("Cliente")
        self.ax_wait.set_ylabel("Tiempo")
        self.figure.tight_layout(pad=2.0)
        self.canvas.draw_idle()

    def set_status(self, text: str):
        self.status_var.set(text)

    def show_error(self, message: str):
        messagebox.showerror("Error", message)
