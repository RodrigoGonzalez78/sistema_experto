from fastlite import Database
from dataclasses import dataclass

# 1. Definimos el esquema usando un Dataclass
# FastLite convertirá automáticamente el nombre 'LearningLogs' 
# a la tabla 'learning_logs' en la base de datos.
@dataclass
class LearningLogs:
    id: int
    timestamp: str
    system_used: str
    inputs: str
    diagnosis: str
    user_feedback: str
    corrected: bool

def get_db():
    # Crea o conecta a la base de datos
    db = Database('expert_data.db')
    
    # 2. Creamos la tabla pasando la CLASE, no un string
    if "learning_logs" not in db.t:
        db.create(LearningLogs, pk="id")
    
    return db