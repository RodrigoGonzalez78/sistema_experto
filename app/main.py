from fasthtml.common import *
import json
from datetime import datetime

# Imports internos
from app.database import get_db
from app.systems.deterministic import RuleBasedEngine
from app.systems.probabilistic import BayesianEngine
from app.systems.fuzzy_logic import FuzzyEngine

app, rt = fast_app(hdrs=(picolink,))
db = get_db()
Logs = db.t.learning_logs

engines = {
    "deterministico": RuleBasedEngine(),
    "probabilistico": BayesianEngine(),
    "difuso": FuzzyEngine()
}

# --- NUEVOS COMPONENTES VISUALES ---

def ReasoningStep(text, step_num):
    """Renderiza un paso del razonamiento con estilo limpio (tema oscuro)"""
    # Detectar si es un separador
    if text.strip() == "---":
        return Hr(style="border-color: #444; margin: 10px 0;")
    
    return Div(
        Span(f"{step_num}.", style="font-size: 1.1em; margin-right: 12px; color: #888; font-weight: bold; min-width: 25px;"),
        Span(text, style="color: #e0e0e0;"),
        style="padding: 10px 12px; border-left: 3px solid #444; margin-bottom: 6px; background-color: #2d2d2d; border-radius: 4px; display: flex; align-items: flex-start;"
    )

def DiagnosisCard(diag, system_name, inputs):
    inputs_json = json.dumps(inputs)
    
    # Colores semánticos
    is_danger = "DENGUE" in diag.label.upper() or diag.confidence > 0.7
    header_color = "#d93526" if is_danger else "#3e8ed0"
    
    return Article(
        Header(
            Div(
                Small(f"Motor utilizado: {system_name.replace('_', ' ').title()}"),
                H2(diag.label, style=f"color: {header_color}; margin-top:0;"),
                style="display: flex; flex-direction: column;"
            )
        ),
        
        # Barra de Confianza Visual
        Label(f"Nivel de Certeza: {diag.confidence:.1%}"),
        Progress(value=str(int(diag.confidence*100)), max="100"),
        
        # Sección de Explicabilidad (XAI) - Tema Oscuro
        Details(
            Summary("Ver proceso de decision (Paso a paso)", style="color: #e0e0e0; cursor: pointer;"),
            Div(
                *[ReasoningStep(step, i+1) for i, step in enumerate(diag.reasoning)],
                style="margin-top: 10px; padding: 15px; background-color: #1e1e1e; border-radius: 8px;"
            ),
            open=True,
            style="background-color: #252525; padding: 15px; border-radius: 10px; border: 1px solid #333;"
        ),
        
        Footer(
            Form(
                Input(type="hidden", name="system_used", value=system_name),
                Input(type="hidden", name="diagnosis", value=diag.label),
                Input(type="hidden", name="inputs", value=inputs_json),
                Grid(
                    Button("Correcto (Aprender)", name="correct", value="true", cls="outline"),
                    Button("Incorrecto", name="correct", value="false", cls="outline secondary")
                ),
                hx_post="/learn",
                hx_target="#learning-msg"
            ),
            Div(id="learning-msg", style="margin-top:10px; font-weight:bold;")
        )
    )

# --- RUTAS ---
# (El resto de las rutas /, /diagnose, /learn se mantienen similares, 
#  pero asegúrate de que /diagnose llame al nuevo DiagnosisCard)

@rt("/")
def get():
    # Componente reutilizable para sliders
    def Slider(name, label, id_prefix):
        return Div(
            Label(label, style="font-weight: 500; margin-bottom: 5px; display: block;"),
            Div(
                Input(type="range", name=name, min="0", max="10", value="5", 
                      id=f"{id_prefix}-slider", 
                      oninput=f"document.getElementById('{id_prefix}-value').textContent = this.value"),
                Span(id=f"{id_prefix}-value", style="font-weight: bold; margin-left: 10px; min-width: 20px;"),
                Span(" / 10", style="color: #888;"),
                style="display: flex; align-items: center;"
            ),
            style="margin-bottom: 12px;"
        )
    
    return Titled("Sistema Experto Médico IA",
        Container(
            Hgroup(H1("Asistente de Diagnóstico"), H3("TP4 - Integración Simbólica y Probabilística")),
            
            # Formulario de Sensores (Inputs)
            Form(
                Grid(
                    Label("Temperatura (°C)", Input(type="number", name="fiebre", step="0.1", value="38.5")),
                    Label("Motor de Inferencia", Select(
                        Option("Experta (Reglas)", value="deterministico"),
                        Option("Pgmpy (Bayesiano)", value="probabilistico"),
                        Option("Scikit-Fuzzy (Difuso)", value="difuso"),
                        name="engine"
                    ))
                ),
                
                # Sensores binarios (checkboxes)
                Fieldset(
                    Legend("Sensores / Contexto Epidemiológico"),
                    Label(Input(type="checkbox", name="tos"), " Presencia de Tos"),
                    Label(Input(type="checkbox", name="dolor_garganta"), " Dolor de Garganta"),
                    Label(Input(type="checkbox", name="dolor_cabeza_check"), " Dolor de Cabeza"),
                    Label(Input(type="checkbox", name="viaje_brasil", checked=True), " Viaje reciente a Brasil"),
                    Label(Input(type="checkbox", name="contacto_dengue", checked=True), " Contacto con positivo de Dengue"),
                    Label(Input(type="checkbox", name="vive_corrientes", checked=True), " Reside en Corrientes"),
                    Label(Input(type="checkbox", name="verano", checked=True), " Estación actual: Verano"),
                ),
                
                # Seccion exclusiva para Sistema Difuso
                Fieldset(
                    Legend("Variables Difusas (Gradientes 0-10)"),
                    Small("Estos sliders son especialmente relevantes para el motor de Lógica Difusa", 
                          style="color: #888; display: block; margin-bottom: 15px;"),
                    Grid(
                        Slider("intensidad_dolor_cabeza", "Intensidad Dolor de Cabeza", "dolor-cabeza"),
                        Slider("intensidad_tos", "Intensidad de Tos", "tos"),
                    ),
                    style="background-color: #1a1a2e; border: 1px solid #444; border-radius: 8px; padding: 20px;"
                ),
                Button("Analizar Paciente", type="submit"),
                hx_post="/diagnose",
                hx_target="#results"
            ),
            Br(),
            Div(id="results")
        )
    )

@rt("/diagnose")
async def post(req):
    form = await req.form()
    # Mapeo de inputs
    facts = {
        'fiebre': float(form.get('fiebre', 36)),
        # Variables difusas (sliders 0-10)
        'intensidad_dolor_cabeza': float(form.get('intensidad_dolor_cabeza', 5)),
        'intensidad_tos': float(form.get('intensidad_tos', 5)),
        # Variables binarias
        'tos': form.get('tos') == "on",
        'dolor_garganta': form.get('dolor_garganta') == "on",
        'dolor_cabeza': form.get('dolor_cabeza_check') == "on",
        'viaje_brasil': form.get('viaje_brasil') == "on",
        'contacto_dengue': form.get('contacto_dengue') == "on",
        'vive_corrientes': form.get('vive_corrientes') == "on",
        'verano': form.get('verano') == "on"
    }
    
    engine_name = form.get('engine')
    if engine_name in engines:
        # Inferencia
        prediction = engines[engine_name].infer(facts)
        # Renderizado visual mejorado
        return DiagnosisCard(prediction, engine_name, facts)
    
    return P("Error: Motor no encontrado")

@rt("/learn")
async def post(req):
    # (Misma lógica de persistencia que antes)
    form = await req.form()
    Logs.insert({
        "timestamp": datetime.now().isoformat(),
        "system_used": form.get("system_used"),
        "inputs": form.get("inputs"),
        "diagnosis": form.get("diagnosis"),
        "user_feedback": form.get("feedback"),
        "corrected": form.get("correct") == "true"
    })
    return P("Conocimiento registrado.", style="color: green;")

if __name__ == "__main__":
    serve()