from experta import *
from typing import Dict, Any
from .base import InferenceEngine, Diagnosis

# --- DEFINICIÓN DE HECHOS ---
class Sintomas(Fact):
    """Información sobre síntomas del paciente"""
    pass

class Epidemiologia(Fact):
    """Información de contexto"""
    pass

# --- MOTOR DE CONOCIMIENTO ---
class DiagnosticoMedico(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.trace = []  # Traza para explicar al usuario
        self.conclusion = None
        self.confidence = 0.0

    def log(self, text):
        self.trace.append(text)

    # ----------------------------------------------------------------
    # REGLA 1: Evaluar Síntomas
    # ESTRATEGIA: Capturamos f (fiebre), t (tos), g (garganta) usando MATCH
    # y evaluamos la lógica DENTRO de la función.
    # ----------------------------------------------------------------
    @Rule(Sintomas(fiebre=MATCH.f, tos=MATCH.t, dolor_garganta=MATCH.g, dolor_cabeza=MATCH.dc))
    def regla_sintomas_base(self, f, t, g, dc):
        # Lógica en Python (Más segura que ponerla en el decorador)
        tiene_fiebre = f > 37.5
        sintoma_respiratorio = t or g
        tiene_dolor_cabeza = dc

        if tiene_fiebre and (sintoma_respiratorio or tiene_dolor_cabeza):
            self.log("REGLA ACTIVADA: regla_sintomas_base")
            self.log(f"   Condición: Fiebre {f}°C (>37.5) Y (Tos={t} O Garganta={g} O DolorCabeza={dc})")
            self.log("   Resultado: Sospecha de infección viral detectada.")
            self.declare(Fact(sospecha_infeccion=True))
        else:
            self.log("REGLA EVALUADA: regla_sintomas_base (No se cumplió)")

    # ----------------------------------------------------------------
    # REGLA 2: Evaluar Nexo Epidemiológico
    # Capturamos TODAS las variables de Epidemiologia para asegurar el 'match'
    # ----------------------------------------------------------------
    @Rule(Fact(sospecha_infeccion=True),
          Epidemiologia(viaje_brasil=MATCH.v, contacto_dengue=MATCH.c, 
                        vive_corrientes=MATCH.vc, verano=MATCH.ver))
    def regla_nexo_dengue(self, v, c, vc, ver):
        # Evaluamos si hay viaje O contacto
        if v or c:
            self.log("REGLA ACTIVADA: regla_nexo_dengue")
            self.log(f"   Condición: (Viaje={v} OR Contacto={c})")
            self.log("   Resultado: Riesgo epidemiológico ALTO.")
            self.declare(Fact(riesgo_dengue=True))
        else:
            self.log("REGLA EVALUADA: regla_nexo_dengue (Sin nexo epidemiológico)")

    # ----------------------------------------------------------------
    # REGLA 3: Confirmación por Contexto Local
    # ----------------------------------------------------------------
    @Rule(Fact(riesgo_dengue=True),
          Epidemiologia(vive_corrientes=MATCH.vc, verano=MATCH.ver, 
                        viaje_brasil=W(), contacto_dengue=W()))  # W() = wildcard (ignora el valor)
    def regla_confirmacion_contexto(self, vc, ver):
        if vc and ver:
            self.log("REGLA ACTIVADA: regla_confirmacion_contexto")
            self.log("   Condición: Vive en Corrientes Y es Verano")
            self.log("   Resultado: DENGUE (Alta Probabilidad)")
            self.conclusion = "DENGUE (Alta Probabilidad)"
            self.confidence = 0.95
        else:
            # Caso donde hay riesgo pero no es contexto local (ej: caso importado)
            self.log(" Riesgo Dengue detectado, pero contexto local no aplica.")
            self.conclusion = "Sospecha de Dengue (Importado)"
            self.confidence = 0.80

    # ----------------------------------------------------------------
    # REGLA 4: COVID por Descarte
    # Se activa si hay infección PERO NO se declaró riesgo_dengue
    # ----------------------------------------------------------------
    @Rule(Fact(sospecha_infeccion=True),
          NOT(Fact(riesgo_dengue=True)))
    def regla_covid_por_descarte(self):
        self.log("REGLA ACTIVADA: regla_covid_por_descarte")
        self.log("   Condición: Hay síntomas pero NO hay nexo de Dengue.")
        self.log("   Resultado: Posible COVID-19")
        self.conclusion = "Posible COVID-19"
        self.confidence = 0.60

# --- CLASE INTERFAZ ---
class RuleBasedEngine(InferenceEngine):
    def infer(self, facts: Dict[str, Any]) -> Diagnosis:
        engine = DiagnosticoMedico()
        engine.reset()
        
        # Cargamos los hechos tal cual vienen del formulario
        engine.declare(Sintomas(
            fiebre=facts.get('fiebre', 36.5), 
            tos=facts.get('tos', False), 
            dolor_garganta=facts.get('dolor_garganta', False),
            dolor_cabeza=facts.get('dolor_cabeza', False)
        ))
        
        engine.declare(Epidemiologia(
            viaje_brasil=facts['viaje_brasil'],
            contacto_dengue=facts['contacto_dengue'],
            vive_corrientes=facts['vive_corrientes'],
            verano=facts['verano']
        ))
        
        engine.run()
        
        label = engine.conclusion if engine.conclusion else "Sin Diagnóstico Concluyente"
        # Si no hay conclusión, la confianza es 0.0
        conf = engine.confidence if engine.conclusion else 0.0
        
        return Diagnosis(label, conf, engine.trace)