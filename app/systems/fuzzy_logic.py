import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from .base import InferenceEngine, Diagnosis

class FuzzyEngine(InferenceEngine):
    def __init__(self):
        # Definición del universo
        self.fiebre = ctrl.Antecedent(np.arange(35, 42, 0.1), 'fiebre')
        self.riesgo_epi = ctrl.Antecedent(np.arange(0, 11, 1), 'riesgo_epi')
        self.posibilidad = ctrl.Consequent(np.arange(0, 101, 1), 'posibilidad_dengue')

        # Funciones de membresía
        self.fiebre['alta'] = fuzz.trapmf(self.fiebre.universe, [38, 39, 42, 42])
        self.fiebre['media'] = fuzz.trimf(self.fiebre.universe, [36, 37.5, 38.5])
        
        self.riesgo_epi['alto'] = fuzz.trapmf(self.riesgo_epi.universe, [6, 8, 10, 10])
        self.riesgo_epi['bajo'] = fuzz.trimf(self.riesgo_epi.universe, [0, 0, 5])

        self.posibilidad['alta'] = fuzz.trimf(self.posibilidad.universe, [60, 100, 100])
        self.posibilidad['baja'] = fuzz.trimf(self.posibilidad.universe, [0, 0, 40])

        # Reglas
        self.ctrl = ctrl.ControlSystem([
            ctrl.Rule(self.fiebre['alta'] & self.riesgo_epi['alto'], self.posibilidad['alta']),
            ctrl.Rule(self.riesgo_epi['bajo'], self.posibilidad['baja'])
        ])
        self.sim = ctrl.ControlSystemSimulation(self.ctrl)

    def infer(self, facts: dict[str, any]) -> Diagnosis:
        try:
            # Calcular puntaje epi
            epi_score = 0
            if facts['viaje_brasil']: epi_score += 5
            if facts['contacto_dengue']: epi_score += 5

            self.sim.input['fiebre'] = float(facts['fiebre'])
            self.sim.input['riesgo_epi'] = epi_score
            self.sim.compute()
            
            result = self.sim.output['posibilidad_dengue']
            return Diagnosis(
                "Positivo Dengue" if result > 50 else "Negativo",
                result / 100,
                [f"Fiebre: {facts['fiebre']}", f"Score Epi: {epi_score}", f"Defuzzificación: {result:.2f}%"]
            )
        except:
            return Diagnosis("Error Difuso", 0.0, ["Datos fuera de rango"])