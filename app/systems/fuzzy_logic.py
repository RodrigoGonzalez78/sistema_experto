import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from .base import InferenceEngine, Diagnosis

class FuzzyEngine(InferenceEngine):
    def __init__(self):
        # Definicion del universo de discurso para cada variable
        self.fiebre = ctrl.Antecedent(np.arange(35, 42.1, 0.1), 'fiebre')
        self.dolor_cabeza = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'dolor_cabeza')
        self.intensidad_tos = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'intensidad_tos')
        self.riesgo_epi = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'riesgo_epi')
        self.posibilidad = ctrl.Consequent(np.arange(0, 101, 1), 'posibilidad_dengue')

        # Funciones de membresia - Fiebre
        self.fiebre['normal'] = fuzz.trapmf(self.fiebre.universe, [35, 35, 36.5, 37.5])
        self.fiebre['media'] = fuzz.trimf(self.fiebre.universe, [36.5, 37.5, 38.5])
        self.fiebre['alta'] = fuzz.trapmf(self.fiebre.universe, [37.5, 38.5, 42, 42])
        
        # Funciones de membresia compartidas para sintomas (dolor cabeza, tos)
        for var in [self.dolor_cabeza, self.intensidad_tos]:
            var['leve'] = fuzz.trapmf(var.universe, [0, 0, 2, 4])
            var['moderado'] = fuzz.trimf(var.universe, [3, 5, 7])
            var['severo'] = fuzz.trapmf(var.universe, [6, 8, 10, 10])
        
        # Funciones de membresia - Riesgo Epidemiologico
        self.riesgo_epi['bajo'] = fuzz.trapmf(self.riesgo_epi.universe, [0, 0, 2, 4])
        self.riesgo_epi['medio'] = fuzz.trimf(self.riesgo_epi.universe, [3, 5, 7])
        self.riesgo_epi['alto'] = fuzz.trapmf(self.riesgo_epi.universe, [6, 8, 10, 10])

        # Funciones de membresia - Posibilidad Dengue
        self.posibilidad['baja'] = fuzz.trapmf(self.posibilidad.universe, [0, 0, 20, 40])
        self.posibilidad['media'] = fuzz.trimf(self.posibilidad.universe, [30, 50, 70])
        self.posibilidad['alta'] = fuzz.trapmf(self.posibilidad.universe, [60, 80, 100, 100])

        # Reglas difusas - combinando sintomas
        self.ctrl = ctrl.ControlSystem([
            # ALTA: Combinaciones severas
            ctrl.Rule(self.fiebre['alta'] & self.dolor_cabeza['severo'] & self.riesgo_epi['alto'], self.posibilidad['alta']),
            ctrl.Rule(self.fiebre['alta'] & self.dolor_cabeza['severo'], self.posibilidad['alta']),
            ctrl.Rule(self.dolor_cabeza['severo'] & self.intensidad_tos['severo'] & self.riesgo_epi['alto'], self.posibilidad['alta']),
            ctrl.Rule(self.fiebre['alta'] & self.riesgo_epi['alto'], self.posibilidad['alta']),
            
            # MEDIA: Combinaciones moderadas
            ctrl.Rule(self.fiebre['alta'] & self.dolor_cabeza['moderado'], self.posibilidad['media']),
            ctrl.Rule(self.fiebre['media'] & self.dolor_cabeza['moderado'], self.posibilidad['media']),
            ctrl.Rule(self.intensidad_tos['moderado'] & self.dolor_cabeza['moderado'], self.posibilidad['media']),
            ctrl.Rule(self.fiebre['media'] & self.riesgo_epi['medio'], self.posibilidad['media']),
            
            # BAJA: Sintomas leves
            ctrl.Rule(self.fiebre['normal'] & self.dolor_cabeza['leve'] & self.intensidad_tos['leve'], self.posibilidad['baja']),
            ctrl.Rule(self.dolor_cabeza['leve'] & self.riesgo_epi['bajo'], self.posibilidad['baja']),
            ctrl.Rule(self.fiebre['normal'] & self.intensidad_tos['leve'], self.posibilidad['baja']),
            
            # Regla por defecto
            ctrl.Rule(self.fiebre['normal'] | self.fiebre['media'] | self.fiebre['alta'], self.posibilidad['media'])
        ])
        self.sim = ctrl.ControlSystemSimulation(self.ctrl)

    def infer(self, facts: dict[str, any]) -> Diagnosis:
        try:
            trace = []
            
            # Descripcion del sistema difuso
            trace.append("SISTEMA DIFUSO: Variables Linguisticas")
            trace.append("ANTECEDENTES:")
            trace.append("  - Fiebre: [35-42]C -> {normal, media, alta}")
            trace.append("  - Dolor_Cabeza: [0-10] -> {leve, moderado, severo}")
            trace.append("  - Intensidad_Tos: [0-10] -> {leve, moderado, severo}")
            trace.append("  - Riesgo_Epi: [0-10] -> {bajo, medio, alto}")
            trace.append("CONSECUENTE:")
            trace.append("  - Posibilidad_Dengue: [0-100]% -> {baja, media, alta}")
            trace.append("---")
            
            # Obtener valores de los sliders
            dolor_cabeza = float(facts.get('intensidad_dolor_cabeza', 5))
            intensidad_tos = float(facts.get('intensidad_tos', 5))
            
            # Calcular puntaje epi
            epi_score = 0
            if facts['viaje_brasil']: epi_score += 5
            if facts['contacto_dengue']: epi_score += 5
            
            trace.append("VALORES DE ENTRADA (Crisp):")
            trace.append(f"  - Fiebre = {facts['fiebre']}C")
            trace.append(f"  - Dolor_Cabeza = {dolor_cabeza}/10")
            trace.append(f"  - Intensidad_Tos = {intensidad_tos}/10")
            trace.append(f"  - Riesgo_Epi = {epi_score} (Viaje:{'+5' if facts['viaje_brasil'] else '0'}, Contacto:{'+5' if facts['contacto_dengue'] else '0'})")
            trace.append("---")

            # Asignar inputs al simulador
            self.sim.input['fiebre'] = float(facts['fiebre'])
            self.sim.input['dolor_cabeza'] = dolor_cabeza
            self.sim.input['intensidad_tos'] = intensidad_tos
            self.sim.input['riesgo_epi'] = epi_score
            self.sim.compute()
            
            result = self.sim.output['posibilidad_dengue']
            
            trace.append("REGLAS DIFUSAS:")
            trace.append("  [ALTA] Fiebre=alta AND DolorCab=severo AND Riesgo=alto")
            trace.append("  [ALTA] Fiebre=alta AND DolorCab=severo")
            trace.append("  [ALTA] DolorCab=severo AND Tos=severo AND Riesgo=alto")
            trace.append("  [ALTA] Fiebre=alta AND Riesgo=alto")
            trace.append("  [MEDIA] Fiebre=alta AND DolorCab=moderado")
            trace.append("  [MEDIA] Fiebre=media AND DolorCab=moderado")
            trace.append("  [MEDIA] Tos=moderado AND DolorCab=moderado")
            trace.append("  [BAJA] Fiebre=normal AND DolorCab=leve AND Tos=leve")
            trace.append("  [BAJA] DolorCab=leve AND Riesgo=bajo")
            trace.append("---")
            trace.append("DEFUZZIFICACION:")
            trace.append(f"  Metodo: Centroide")
            trace.append(f"  Salida: {result:.2f}%")
            
            if result > 65:
                label = "ALTA Probabilidad Dengue"
            elif result > 35:
                label = "MEDIA Probabilidad Dengue"
            else:
                label = "BAJA Probabilidad Dengue"
            
            return Diagnosis(label, result / 100, trace)
        except Exception as e:
            return Diagnosis("Error Difuso", 0.0, [f"Error: {str(e)}"])