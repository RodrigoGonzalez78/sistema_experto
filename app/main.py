from fasthtml.common import *
import json
from datetime import datetime

# Importaciones internas
from app.database import get_db
from app.systems.deterministic import RuleBasedEngine
from app.systems.probabilistic import BayesianEngine
from app.systems.fuzzy_logic import FuzzyEngine

# Inicialización
app, rt = fast_app(hdrs=(picolink,))
db = get_db()
Logs = db.t.learning_logs

# Instancia de Motores (Singleton)
engines = {
    "deterministico": RuleBasedEngine(),
    "probabilistico": BayesianEngine(),
    "difuso": FuzzyEngine()
}

# --- UI COMPONENTS ---
def SensorForm():
    return Form(
        Grid(
            Label("Temperatura (°C)", Input(type="number", name="fiebre", step="0.1", value="38.5")),
            Label("Seleccionar Motor", Select(
                Option("Basado en Reglas", value="deterministico"),
                Option("Probabilístico (Bayes)", value="probabilistico"),
                Option("Lógica Difusa", value="difuso"),
                name="engine"
            ))
        ),
        Fieldset(
            Label(Input(type="checkbox", name="tos"), " Tos"),
            Label(Input(type="checkbox", name="dolor_garganta"), " Dolor Garganta"),
            Label(Input(type="checkbox", name="viaje_brasil", checked=True), " Viaje a Brasil"),
            Label(Input(type="checkbox", name="contacto_dengue", checked=True), " Contacto Dengue"),
            Label(Input(type="checkbox", name="vive_corrientes", checked=True), " Vive en Corrientes"),
            Label(Input(type="checkbox", name="verano", checked=True), " Es Verano"),
        ),
        Button("Diagnosticar Paciente", type="submit"),
        hx_post="/diagnose",
        hx_target="#results"
    )

def DiagnosisCard(diag, system_name, inputs):
    # Guardamos los inputs como JSON oculto para el aprendizaje
    inputs_json = json.dumps(inputs)
    
    return Article(
        Header(f"Resultado: {system_name.capitalize()}"),
        H2(diag.label, style="color: #d93526;" if "DENGUE" in diag.label.upper() else "color: #3e8ed0;"),
        Progress(value=str(int(diag.confidence*100)), max="100"),
        P(f"Certeza: {diag.confidence:.2%}"),
        Details(Summary("Explicación del Motor"), Ul(*[Li(x) for x in diag.reasoning])),
        Footer(
            Form(
                Input(type="hidden", name="system_used", value=system_name),
                Input(type="hidden", name="diagnosis", value=diag.label),
                Input(type="hidden", name="inputs", value=inputs_json),
                Label("Validación Humana (Aprendizaje):", 
                      Input(name="feedback", placeholder="¿Diagnóstico correcto? Comentarios...")),
                Grid(
                    Button("Confirmar (Aprender)", name="correct", value="true"),
                    Button("Marcar Error", name="correct", value="false", cls="secondary")
                ),
                hx_post="/learn",
                hx_target="#learning-msg"
            ),
            Div(id="learning-msg")
        )
    )

# --- RUTAS ---
@rt("/")
def get():
    stats = f"Casos aprendidos en BD: {Logs.count}"
    return Titled("TP4: IA Simbólica & Diagnóstico Médico",
        Container(
            Hgroup(H1("Sistema Experto Epidemiológico"), H3("Dengue vs COVID-19")),
            SensorForm(),
            Div(id="results"),
            Hr(),
            P(stats, style="font-size: small; color: grey;")
        )
    )

@rt("/diagnose")
async def post(req):
    form = await req.form()
    
    # 1. Parsear Inputs (Simulación de Sensores)
    facts = {
        'fiebre': float(form.get('fiebre', 36)),
        'tos': form.get('tos') == "on",
        'dolor_garganta': form.get('dolor_garganta') == "on",
        'viaje_brasil': form.get('viaje_brasil') == "on",
        'contacto_dengue': form.get('contacto_dengue') == "on",
        'vive_corrientes': form.get('vive_corrientes') == "on",
        'verano': form.get('verano') == "on"
    }
    
    # 2. Invocar Motor
    engine_name = form.get('engine')
    if engine_name in engines:
        prediction = engines[engine_name].infer(facts)
        return DiagnosisCard(prediction, engine_name, facts)
    
    return P("Error: Motor no encontrado", style="color:red")

@rt("/learn")
async def post(req):
    form = await req.form()
    
    # 3. Persistencia (Aprendizaje)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "system_used": form.get("system_used"),
        "inputs": form.get("inputs"),
        "diagnosis": form.get("diagnosis"),
        "user_feedback": form.get("feedback"),
        "corrected": form.get("correct") == "true"
    }
    
    Logs.insert(log_entry)
    
    return P("✅ Feedback registrado en Base de Conocimiento. El sistema aprenderá de este caso.", 
             style="color: green; font-weight: bold; margin-top: 10px;")

serve()