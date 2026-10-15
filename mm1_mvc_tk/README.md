# Simulador M/M/1 con SimPy, MVC y Tkinter

Práctica de Simulación: **Sistema de líneas de espera M/M/1 mediante SimPy**.

## Objetivo

Implementar un sistema M/M/1 con:
- llegadas exponenciales / proceso de Poisson;
- tiempos de servicio exponenciales;
- un solo servidor;
- disciplina FIFO;
- cálculo de métricas teóricas;
- simulación de tiempo promedio de espera y tamaño promedio de cola;
- comparación entre resultados teóricos y simulados;
- gráficas locales con Tkinter + Matplotlib.

## Arquitectura

Se aplica **MVC**:

- **Model**: lógica de simulación y cálculo de métricas.
- **View**: interfaz gráfica local con Tkinter.
- **Controller**: valida entradas, coordina Model y View.

Además se aplican patrones básicos:

1. **Strategy**: `MM1TheoryStrategy` encapsula el cálculo teórico del modelo.
2. **Factory**: `ScenarioFactory` construye los tres escenarios propuestos y un escenario personalizado.

## Estructura

```text
mm1_mvc_tk/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── docs/
│   ├── arquitectura.md
│   ├── roles_equipo.md
│   └── flujo_git.md
├── src/
│   ├── analyzers/
│   │   └── result_analyzer.py
│   ├── controllers/
│   │   └── simulation_controller.py
│   ├── models/
│   │   └── mm1_model.py
│   ├── patterns/
│   │   ├── scenario_factory.py
│   │   └── theory_strategy.py
│   └── views/
│       └── main_view.py
└── tests/
    └── test_theory.py
```

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

> En Ubuntu, si Tkinter no está instalado:
>
> ```bash
> sudo apt install python3-tk
> ```

## Escenarios

| Escenario | λ | μ | Condición |
|---|---:|---:|---|
| 1 | 2.0 | 3.0 | Sistema estable |
| 2 | 2.5 | 3.0 | Mayor utilización |
| 3 | 2.9 | 3.0 | Cerca de saturación |

La interfaz también permite introducir valores personalizados.

## Métricas

Se calculan:

- `ρ = λ / μ`
- `L = λ / (μ - λ)`
- `Lq = λ² / (μ(μ - λ))`
- `W = 1 / (μ - λ)`
- `Wq = λ / (μ(μ - λ))`
- tiempo promedio de espera simulado;
- tamaño promedio de cola simulado.

Para estabilidad se valida `λ < μ`.

## Ejecución de pruebas

```bash
python -m unittest discover -s tests -v
```

## Nota sobre la guía

En una línea del fundamento teórico aparece `ρ = μ / λ`, pero el pseudocódigo de la misma guía usa `ρ = λ / μ`. Este proyecto usa `ρ = λ / μ`, que además es consistente con la condición de estabilidad `λ < μ`.

## Trabajo colaborativo

El flujo de trabajo recomendado usa:
- `main`: versión estable;
- `develop`: integración;
- ramas `feature/...` por integrante;
- Pull Requests antes de fusionar cambios.

Ver `docs/roles_equipo.md` y `docs/flujo_git.md`.


## Analyzer y tabla comparativa

Cada vez que se ejecuta un escenario, `ResultAnalyzer` registra:

- ρ
- L
- Lq
- W
- Wq
- tiempo promedio de espera simulado
- tamaño promedio de la cola simulado

Los resultados se guardan automáticamente en:

```text
results/resultados_escenarios.csv
```

La interfaz también incluye una tabla **Analyzer - Comparación de resultados**
y un botón para ejecutar y comparar automáticamente los tres escenarios.
