from .base import InferenceEngine, Diagnosis

class BayesianEngine(InferenceEngine):
    def __init__(self):
        # Priors iniciales basados en el contexto (Verano en Corrientes)
        self.priors = {'Dengue': 0.4, 'COVID': 0.3, 'Otro': 0.3}
        self.likelihoods = {
            'fiebre_alta':   {'Dengue': 0.9, 'COVID': 0.8, 'Otro': 0.2},
            'nexo_epi':      {'Dengue': 0.85, 'COVID': 0.1, 'Otro': 0.05}, # Nexo fuerte
            'tos':           {'Dengue': 0.2, 'COVID': 0.9, 'Otro': 0.4}
        }

    def infer(self, facts: dict[str, any]) -> Diagnosis:
        posteriors = self.priors.copy()
        trace = [f"Priors: {posteriors}"]
        
        # Detectar evidencias
        evidences = []
        if facts['fiebre'] > 38: evidences.append('fiebre_alta')
        if facts['viaje_brasil'] or facts['contacto_dengue']: evidences.append('nexo_epi')
        if facts['tos']: evidences.append('tos')

        # Algoritmo de Actualización
        for ev in evidences:
            norm = 0
            temp = {}
            for h in posteriors:
                # P(H|E) ~ P(E|H) * P(H)
                val = posteriors[h] * self.likelihoods[ev][h]
                temp[h] = val
                norm += val
            
            # Normalización
            if norm > 0:
                for h in posteriors: posteriors[h] = temp[h] / norm
            
            trace.append(f"Evidencia '{ev}' -> Dengue: {posteriors['Dengue']:.2f}, COVID: {posteriors['COVID']:.2f}")

        # Selección MAP (Maximum A Posteriori)
        best = max(posteriors, key=posteriors.get)
        return Diagnosis(best.upper(), round(posteriors[best], 2), trace)