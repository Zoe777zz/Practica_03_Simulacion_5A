# Simulador M/M/1 — Vista Web

Práctica 03 de **Simulación de un sistema de líneas de espera M/M/1 mediante SimPy**.

La versión final usa una **vista web local con Flask**, una paleta visual azul y una animación interactiva de la cola. La lógica continúa separada mediante **MVC** y patrones básicos de diseño.

## Características

- Tres escenarios fijos definidos por la práctica:
  - Escenario 1: λ = 2.0, μ = 3.0.
  - Escenario 2: λ = 2.5, μ = 3.0.
  - Escenario 3: λ = 2.9, μ = 3.0.
- El usuario solo indica **N**, número de repeticiones.
- En cada repetición se genera automáticamente **una semilla**, compartida por los tres escenarios.
- Los resultados se calculan y mantienen **en memoria**; no se crean CSV ni archivos de resultados.
- Tabla comparativa con:
  - ρ
  - L
  - Lq
  - W
  - Wq
  - tiempo promedio de espera simulado
  - tamaño promedio de cola simulado
- Gráficas de:
  - comportamiento de la cola en el tiempo;
  - tiempo de espera en el tiempo;
  - ρ observado y teórico relacionado con tiempo de espera y tiempo de ejecución/servicio.
- Animación web conceptual en cuatro etapas: llegada → cola FIFO → atención → salida.
- Patrones utilizados:
  - **Strategy** para las métricas teóricas M/M/1;
  - **Factory** para los escenarios fijos.

## Arquitectura

```text
Navegador (HTML / CSS / JS)
          │
          ▼
Flask / Controller
          │
          ├──────────► ScenarioFactory
          │
          ▼
MM1Model (SimPy)
          │
          ├──────────► MM1TheoryStrategy
          │
          ▼
ResultAnalyzer (memoria)
          │
          ▼
ChartView (Matplotlib en memoria)
          │
          ▼
JSON + imágenes base64 → Navegador
```

## Estructura del proyecto

```text
mm1_web_final/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
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
│       └── chart_view.py
├── tests/
│   ├── test_theory.py
│   └── test_web.py
└── docs/
    ├── arquitectura.md
    ├── flujo_git.md
    └── roles_equipo.md
```

# Cómo clonar y ejecutar

## 1. Clonar el repositorio

Reemplaza `URL_DEL_REPOSITORIO` por el enlace real de GitHub:

```bash
git clone URL_DEL_REPOSITORIO
cd mm1_web_final
```

## 2. Crear el entorno virtual

### Linux / Ubuntu / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
py -m venv .venv
.venv\Scripts\activate.bat
```

Cuando el entorno esté activo normalmente aparecerá `(.venv)` al inicio de la terminal.

## 3. Actualizar pip e instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Ejecutar la aplicación

```bash
python app.py
```

En Linux también puedes usar:

```bash
python3 app.py
```

Después abre en el navegador:

```text
http://127.0.0.1:5000
```

Para detener el servidor usa `Ctrl + C` en la terminal.

# Ejecutar pruebas

```bash
python -m unittest discover -s tests -v
```

# Flujo Git recomendado para 4 integrantes

```text
main
└── develop
    ├── feature/modelo-simpy
    ├── feature/vista-web
    ├── feature/controlador-patrones
    └── feature/pruebas-documentacion
```

Cada integrante debe crear su rama desde `develop`, realizar commits pequeños y abrir un Pull Request hacia `develop`. Cuando la versión integrada esté verificada, se fusiona `develop` hacia `main`.

## Nota sobre ρ

La guía contiene dos expresiones diferentes: en el fundamento teórico aparece `ρ = μ / λ`, mientras que el pseudocódigo indica `ρ = λ / μ`. La aplicación sigue la expresión del pseudocódigo, `ρ = λ / μ`, coherente además con la condición de estabilidad indicada en la misma guía: `λ < μ`.
