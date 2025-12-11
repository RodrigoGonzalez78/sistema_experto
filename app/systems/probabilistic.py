from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from typing import Dict, Any
# Asegurate de importar tus clases base correctamente según tu estructura de carpetas
from .base import InferenceEngine, Diagnosis 

class BayesianEngine(InferenceEngine):
    def __init__(self):
        # 1. Definir la Estructura (Causa -> Efecto)
        # Agregamos 'Nexo' como causa principal.
        # Agregamos 'Tos' y 'DolorGarganta' que tenías en la pantalla pero no en la red.
        self.model = DiscreteBayesianNetwork([
            ('Nexo', 'Dengue'),          # Nexo Epidemiológico causa probabilidad de Dengue
            ('Dengue', 'Fiebre'),
            ('Dengue', 'DolorCabeza'),
            ('Dengue', 'DolorCuerpo'),
            ('Dengue', 'Tos'),           # Nuevo
            ('Dengue', 'DolorGarganta')  # Nuevo
        ])

        # 2. Definir Tablas de Probabilidad (CPDs)

        # A. Nodo NEXO (Abstrae Viaje, Contacto y Zona)
        # Valores: [0=No hay nexo, 1=Hay nexo]
        # (La prob a priori no importa mucho porque siempre la vamos a setear como evidencia)
        cpd_nexo = TabularCPD(variable='Nexo', variable_card=2, values=[[0.7], [0.3]])

        # B. Nodo DENGUE (Depende del Nexo)
        # Si NO hay nexo: Probabilidad base muy baja (0.05).
        # Si SI hay nexo: Probabilidad alta (0.60) -> Sube mucho la sospecha inicial.
        cpd_dengue = TabularCPD(variable='Dengue', variable_card=2, 
                                values=[[0.95, 0.40],   # P(No Dengue)
                                        [0.05, 0.60]],  # P(Si Dengue)
                                evidence=['Nexo'], evidence_card=[2])

        # C. SÍNTOMAS (Dependen de Dengue)
        
        # Fiebre: Muy común en Dengue
        cpd_fiebre = TabularCPD(variable='Fiebre', variable_card=2, 
                                values=[[0.9, 0.1],  # P(No|No), P(No|Si)
                                        [0.1, 0.9]], # P(Si|No), P(Si|Si)
                                evidence=['Dengue'], evidence_card=[2])

        # Dolor Cabeza: Muy común (Retroocular)
        cpd_cabeza = TabularCPD(variable='DolorCabeza', variable_card=2, 
                                values=[[0.8, 0.15], 
                                        [0.2, 0.85]],
                                evidence=['Dengue'], evidence_card=[2])

        # Dolor Cuerpo: Común ("Quebrantahuesos")
        cpd_cuerpo = TabularCPD(variable='DolorCuerpo', variable_card=2, 
                                values=[[0.8, 0.2], 
                                        [0.2, 0.8]],
                                evidence=['Dengue'], evidence_card=[2])

        # Tos: POCO común en Dengue (es más de Covid/Gripe). 
        # Si tiene Dengue, la prob de tos es baja (0.2).
        cpd_tos = TabularCPD(variable='Tos', variable_card=2, 
                             values=[[0.6, 0.8], 
                                     [0.4, 0.2]], # P(Si|No)=0.4 (Gripe comun), P(Si|Si)=0.2
                             evidence=['Dengue'], evidence_card=[2])

        # Dolor Garganta: POCO común en Dengue.
        cpd_garganta = TabularCPD(variable='DolorGarganta', variable_card=2, 
                                  values=[[0.6, 0.7], 
                                          [0.4, 0.3]], 
                                  evidence=['Dengue'], evidence_card=[2])

        # Agregar CPDs y verificar
        self.model.add_cpds(cpd_nexo, cpd_dengue, cpd_fiebre, cpd_cabeza, cpd_cuerpo, cpd_tos, cpd_garganta)
        self.model.check_model()
        self.inference = VariableElimination(self.model)

    def infer(self, facts: Dict[str, Any]) -> Diagnosis:
        evidence = {}
        trace = []
        
        trace.append("RED BAYESIANA: Estructura Actualizada")
        trace.append("NODOS: Nexo -> Dengue -> {Síntomas}")
        trace.append("---")
        
        # --- 1. LÓGICA DE UNIFICACIÓN DE RIESGO (CRÍTICO) ---
        # Aquí combinamos las variables del TP (Corrientes, Contacto, Viaje) en un solo nodo 'Nexo'
        
        es_verano = facts.get('estacion_verano', False) # Asumiendo que viene del checkbox
        en_corrientes = facts.get('reside_corrientes', False)
        contacto = facts.get('contacto_dengue', False)
        viaje = facts.get('viaje_brasil', False)
        
        tiene_riesgo = False
        razon_riesgo = []

        if viaje:
            tiene_riesgo = True
            razon_riesgo.append("Viaje a Brasil")
        if contacto:
            tiene_riesgo = True
            razon_riesgo.append("Contacto estrecho")
        if en_corrientes and es_verano:
            tiene_riesgo = True
            razon_riesgo.append("Zona Endémica (Corrientes+Verano)")

        if tiene_riesgo:
            evidence['Nexo'] = 1
            trace.append(f"  - Nexo Epidemiológico = 1 (DETECTADO)")
            trace.append(f"    Motivos: {', '.join(razon_riesgo)}")
        else:
            evidence['Nexo'] = 0
            trace.append("  - Nexo Epidemiológico = 0 (No detectado)")

        # --- 2. MAPEO DE SÍNTOMAS ---
        
        # Fiebre
        if facts['fiebre'] > 37.5:
            evidence['Fiebre'] = 1
            trace.append(f"  - Fiebre = 1 (>37.5°C)")
        else:
            evidence['Fiebre'] = 0 # Importante setear el 0 si no tiene fiebre
            
        # Checkboxes simples
        sensores = {
            'dolor_cabeza': 'DolorCabeza', 
            'presencia_tos': 'Tos', 
            'dolor_garganta': 'DolorGarganta'
        }
        
        for key_form, key_nodo in sensores.items():
            if facts.get(key_form):
                evidence[key_nodo] = 1
                trace.append(f"  - {key_nodo} = 1 (Presente)")
            else:
                evidence[key_nodo] = 0
                # No agregamos al trace lo que no está para no ensuciar, o sí si prefieres:
                # trace.append(f"  - {key_nodo} = 0")

        trace.append("---")
        
        # --- 3. INFERENCIA ---
        try:
            # Consultamos la probabilidad de Dengue dada la evidencia acumulada
            result = self.inference.query(variables=['Dengue'], evidence=evidence)
            prob_dengue = result.values[1] # El índice 1 corresponde al estado "1" (Tiene Dengue)
            
            trace.append("CÁLCULO DE PROBABILIDAD POSTERIOR:")
            trace.append(f"  P(Dengue | Evidencia) = {prob_dengue:.2%}")
            
            # Ajuste de etiqueta visual
            if prob_dengue > 0.8:
                label = "ALTA PROBABILIDAD DENGUE"
            elif prob_dengue > 0.4:
                label = "SOSPECHOSO (Probabilidad Media)"
            else:
                label = "Baja Probabilidad Dengue"
                
            return Diagnosis(label, float(prob_dengue), trace)
            
        except Exception as e:
            return Diagnosis("Error en Inferencia", 0.0, [str(e)])