# 🦟 Sistema Experto Epidemiológico

<p align="center">
  <strong>Sistema de diagnóstico inteligente para Dengue vs COVID-19</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastHTML-latest-green.svg" alt="FastHTML">
  <img src="https://img.shields.io/badge/Docker-ready-blue.svg" alt="Docker">
  <img src="https://img.shields.io/badge/pgmpy-Bayesian-orange.svg" alt="pgmpy">
  <img src="https://img.shields.io/badge/experta-Rules-purple.svg" alt="experta">
</p>

---

## 📋 Descripción

Sistema experto que utiliza **Inteligencia Artificial Simbólica y Probabilística** para el diagnóstico diferencial entre Dengue y COVID-19. Implementa tres motores de inferencia diferentes:

| Motor | Librería | Descripción |
|-------|----------|-------------|
| **Determinístico** | `experta` | Basado en reglas IF-THEN con encadenamiento hacia adelante |
| **Probabilístico** | `pgmpy` | Redes Bayesianas con eliminación de variables |
| **Difuso** | `scikit-fuzzy` | Lógica Difusa con funciones de membresía trapezoidales |

### ✨ Características

- 🔬 **Múltiples motores de inferencia** para comparar resultados
- 📊 **Interfaz web interactiva** con tema oscuro moderno
- 🎚️ **Variables difusas** con sliders graduales (0-10)
- ✅ **Checkboxes binarios** para síntomas y contexto epidemiológico
- 🧠 **Explicabilidad (XAI)** - visualización paso a paso del razonamiento
- 💾 **Persistencia de casos** con feedback humano en SQLite
- 🐳 **Soporte Docker** listo para producción

---

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Docker y Docker Compose (opcional)

### Instalación Local

1. **Clonar el repositorio**

```bash
git clone <url-del-repositorio>
cd sistema_experto
```

2. **Crear entorno virtual (recomendado)**

```bash
python -m venv venv
source venv/bin/activate  # En Linux/macOS
# o
.\venv\Scripts\activate   # En Windows
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**

```bash
uvicorn app.main:app --reload --port 5001
```

5. **Acceder a la aplicación**

Abrir en el navegador: [http://localhost:5001](http://localhost:5001)

---

## 🐳 Docker

### Usando Docker Compose (Recomendado)

```bash
# Construir y ejecutar
docker compose up --build

# Ejecutar en segundo plano
docker compose up -d

# Ver logs
docker compose logs -f

# Detener
docker compose down
```

### Nota sobre compatibilidad

El Dockerfile usa Python 3.10 e incluye un parche automático para `frozendict` (dependencia de `experta`) que requiere `collections.abc.Mapping` en Python 3.10+.

---

## 📁 Estructura del Proyecto

```
sistema_experto/
├── app/
│   ├── systems/
│   │   ├── base.py           # Clase abstracta InferenceEngine
│   │   ├── deterministic.py  # Motor Experta (reglas IF-THEN)
│   │   ├── probabilistic.py  # Motor pgmpy (Red Bayesiana)
│   │   └── fuzzy_logic.py    # Motor scikit-fuzzy (Lógica Difusa)
│   ├── database.py           # Configuración FastLite/SQLite
│   └── main.py               # Aplicación FastHTML + rutas
├── data/                     # Datos persistentes (Docker)
├── docker-compose.yml        # Orquestación Docker
├── Dockerfile                # Imagen Docker (Python 3.10)
├── README.md                 # Este archivo
└── requirements.txt          # Dependencias Python
```

---

## 🔧 Variables de Entrada

### Checkboxes (Binarios)
| Variable | Descripción |
|----------|-------------|
| `tos` | Presencia de tos |
| `dolor_garganta` | Dolor de garganta |
| `dolor_cabeza` | Dolor de cabeza |
| `viaje_brasil` | Viaje reciente a zona endémica |
| `contacto_dengue` | Contacto con caso positivo |
| `vive_corrientes` | Reside en zona de riesgo |
| `verano` | Estación actual verano |

### Sliders Difusos (0-10)
| Variable | Descripción |
|----------|-------------|
| `intensidad_dolor_cabeza` | Intensidad del dolor de cabeza |
| `intensidad_tos` | Intensidad de la tos |

---

## 📊 Motores de Inferencia

### 1. Determinístico (Experta)
- Usa encadenamiento hacia adelante (forward chaining)
- Reglas con `MATCH` para capturar variables
- Lógica evaluada dentro de funciones Python

### 2. Probabilístico (pgmpy)
- Red Bayesiana con estructura: `Viaje → Dengue → {Fiebre, DolorCuerpo, DolorCabeza}`
- Inferencia por eliminación de variables
- Calcula P(Dengue | Evidencia)

### 3. Difuso (scikit-fuzzy)
- Antecedentes: Fiebre, Dolor_Cabeza, Intensidad_Tos, Riesgo_Epi
- Consecuente: Posibilidad_Dengue (0-100%)
- Defuzzificación por centroide

---

## 🛠️ Tecnologías

| Librería | Uso |
|----------|-----|
| `python-fasthtml` | Framework web tipo HTMX |
| `uvicorn` | Servidor ASGI |
| `experta` | Motor de reglas (CLIPS-like) |
| `pgmpy` | Redes Bayesianas |
| `scikit-fuzzy` | Lógica difusa |
| `numpy`, `scipy` | Cálculo numérico |
| `pandas` | Manipulación de datos |
| `fastlite` | SQLite simplificado |

---

## 📝 Licencia

Desarrollado como parte del **TP4: Integración Simbólica y Probabilística**.

---

<p align="center">
  <strong>Desarrollado con ❤️ para propósitos educativos</strong>
</p>