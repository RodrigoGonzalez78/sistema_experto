from typing import Callable, List, Dict
from .base import InferenceEngine, Diagnosis

class Rule:
    def __init__(self, name: str, condition: Callable, consequence: Callable, priority: int = 1):
        self.name = name
        self.condition = condition
        self.consequence = consequence
        self.priority = priority

class RuleBasedEngine(InferenceEngine):
    def __init__(self):
        self.rules = []
        self._load_rules()

    def _load_rules(self):
        # R1: Síntomas Respiratorios
        self.rules.append(Rule(
            "R1: Síntomas Generales",
            lambda f: f['fiebre'] > 37.5 and (f['tos'] or f['dolor_garganta']),
            lambda wm: wm.update({'respiratorio': True}), priority=1
        ))
        # R2: Contexto Epidemiológico (Dengue)
        self.rules.append(Rule(
            "R2: Nexo Epidemiológico (Dengue)",
            lambda f: f['viaje_brasil'] or f['contacto_dengue'],
            lambda wm: wm.update({'riesgo_dengue': 'ALTO', 'riesgo_covid': 'BAJO'}), priority=2
        ))
        # R3: Contexto Local
        self.rules.append(Rule(
            "R3: Zona Endémica (Corrientes/Verano)",
            lambda f: f['vive_corrientes'] and f['verano'],
            lambda wm: wm.update({'contexto_favorece_dengue': True}), priority=1
        ))

    def infer(self, facts: Dict[str, any]) -> Diagnosis:
        working_memory = facts.copy()
        trace = []
        
        # Ejecución de reglas ordenadas por prioridad
        for rule in sorted(self.rules, key=lambda r: r.priority):
            if rule.condition(working_memory):
                rule.consequence(working_memory)
                trace.append(f"Regla Activada: {rule.name}")

        # Evaluación final
        if working_memory.get('riesgo_dengue') == 'ALTO':
            if working_memory.get('contexto_favorece_dengue'):
                return Diagnosis("DENGUE (Alta Probabilidad)", 1.0, trace)
            return Diagnosis("Sospecha de Dengue", 0.8, trace)
        elif working_memory.get('respiratorio'):
            return Diagnosis("Posible COVID-19", 0.6, trace)
        
        return Diagnosis("Sin Diagnóstico Claro", 0.0, trace)