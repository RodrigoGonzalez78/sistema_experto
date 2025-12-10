# base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Diagnosis:
    label: str
    confidence: float
    reasoning: List[str]

class InferenceEngine(ABC):
    """Clase Base que obliga a todos los motores a seguir el mismo estándar."""
    
    @abstractmethod
    def infer(self, facts: Dict[str, Any]) -> Diagnosis:
        pass