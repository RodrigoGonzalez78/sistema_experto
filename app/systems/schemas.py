# schemas.py
from pydantic import BaseModel
from typing import List, Optional

# La "Memoria de Trabajo": Datos del paciente actual
class PatientData(BaseModel):
    fiebre: float  # Grados centigrados
    tos: bool
    dolor_garganta: bool
    viaje_brasil: bool
    contacto_dengue: bool
    vive_corrientes: bool
    verano: bool

# Estructura de respuesta del Subsistema de Explicación
class DiagnosisResult(BaseModel):
    sistema: str
    diagnostico: str
    confianza: float # 0.0 a 1.0
    explicacion: List[str] # Traza del razonamiento