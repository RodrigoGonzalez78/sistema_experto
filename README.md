# 🦟 Sistema Experto Epidemiológico

<p align="center">
  <strong>Sistema de diagnóstico inteligente para Dengue vs COVID-19</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastHTML-latest-green.svg" alt="FastHTML">
  <img src="https://img.shields.io/badge/Docker-ready-blue.svg" alt="Docker">
</p>

---

## 📋 Descripción

Sistema experto que utiliza **Inteligencia Artificial Simbólica** para el diagnóstico diferencial entre Dengue y COVID-19. Implementa tres motores de inferencia diferentes:

| Motor | Descripción |
|-------|-------------|
| **Determinístico** | Basado en reglas IF-THEN tradicionales |
| **Probabilístico** | Utiliza Redes Bayesianas para calcular probabilidades |
| **Difuso** | Implementa Lógica Difusa con scikit-fuzzy |

### ✨ Características

- 🔬 **Múltiples motores de inferencia** para comparar resultados
- 📊 **Interfaz web interactiva** con visualización de certeza
- 🧠 **Sistema de aprendizaje** con feedback humano
- 💾 **Persistencia de casos** en base de datos SQLite
- 🐳 **Soporte Docker** para despliegue sencillo

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

1. **Construir y ejecutar**

```bash
docker compose up --build
```

2. **Ejecutar en segundo plano**

```bash
docker compose up -d
```

3. **Ver logs**

```bash
docker compose logs -f
```

4. **Detener la aplicación**

```bash
docker compose down
```

### Usando Docker directamente

1. **Construir la imagen**

```bash
docker build -t sistema-experto .
```

2. **Ejecutar el contenedor**

```bash
docker run -p 5001:5001 -v $(pwd)/data:/app/data sistema-experto
```

---

## 📁 Estructura del Proyecto

```
sistema_experto/
├── app/
│   ├── __pycache__/          # Cache de Python (ignorado)
│   ├── systems/
│   │   ├── base.py           # Clase base para motores
│   │   ├── deterministic.py  # Motor basado en reglas
│   │   ├── probabilistic.py  # Motor bayesiano
│   │   ├── fuzzy_logic.py    # Motor de lógica difusa
│   │   └── schemas.py        # Esquemas Pydantic
│   ├── database.py           # Configuración de base de datos
│   └── main.py               # Aplicación principal FastHTML
├── data/                     # Datos persistentes (Docker)
├── .gitignore                # Archivos ignorados por Git
├── docker-compose.yml        # Configuración Docker Compose
├── Dockerfile                # Imagen Docker
├── README.md                 # Este archivo
└── requirements.txt          # Dependencias Python
```

---

## 🔧 Uso de la Aplicación

### 1. Ingreso de Síntomas

- **Temperatura**: Ingresar temperatura corporal en °C
- **Síntomas**: Marcar los síntomas presentes (tos, dolor de garganta)
- **Factores de riesgo**: Viaje a Brasil, contacto con casos de dengue, etc.

### 2. Seleccionar Motor de Inferencia

- **Basado en Reglas**: Diagnóstico determinístico
- **Probabilístico (Bayes)**: Cálculo de probabilidades condicionales
- **Lógica Difusa**: Manejo de incertidumbre con conjuntos difusos

### 3. Obtener Diagnóstico

El sistema mostrará:
- 🏷️ **Etiqueta de diagnóstico** (Dengue/COVID-19/Otro)
- 📈 **Nivel de certeza** (porcentaje)
- 📝 **Razonamiento** del motor utilizado

### 4. Feedback de Aprendizaje

- Confirmar si el diagnóstico fue correcto
- Agregar comentarios para mejorar el sistema
- Los casos se almacenan para análisis posterior

---

## 🧪 Desarrollo

### Ejecutar en modo desarrollo

```bash
uvicorn app.main:app --reload --port 5001 --host 0.0.0.0
```

### Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `PORT` | Puerto de la aplicación | `5001` |
| `DATABASE_PATH` | Ruta a la base de datos | `expert_data.db` |

---

## 📊 API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Página principal con formulario |
| `POST` | `/diagnose` | Procesa síntomas y retorna diagnóstico |
| `POST` | `/learn` | Registra feedback del usuario |

---

## 🛠️ Tecnologías Utilizadas

- **[FastHTML](https://github.com/AnswerDotAI/fasthtml)** - Framework web moderno para Python
- **[Uvicorn](https://www.uvicorn.org/)** - Servidor ASGI de alto rendimiento
- **[scikit-fuzzy](https://scikit-fuzzy.github.io/)** - Lógica difusa en Python
- **[NumPy](https://numpy.org/)** - Computación numérica
- **[Pydantic](https://docs.pydantic.dev/)** - Validación de datos
- **[FastLite](https://github.com/AnswerDotAI/fastlite)** - SQLite simplificado

---

## 📝 Licencia

Este proyecto fue desarrollado como parte del **TP4: IA Simbólica & Diagnóstico Médico**.

---

## 👥 Contribución

1. Fork del repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

---

<p align="center">
  <strong>Desarrollado con ❤️ para propósitos educativos</strong>
</p>