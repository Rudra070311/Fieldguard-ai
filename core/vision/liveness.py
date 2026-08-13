from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass(frozen=True)
class LivenessResult:
    score: float
    is_live: bool
    model_name: str
    model_version: str

class LivenessService:
    def __init__(
        self,
        model: Any,
        threshold: float = 0.60,
        model_name: str = "liveness",
        model_version: str = "1",
    ) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Invalid liveness threshold.")

        self.model = model
        self.threshold = threshold
        self.model_name = model_name
        self.model_version = model_version

    def predict(self, image: np.ndarray,) -> LivenessResult:
        if image is None or image.size == 0:
            raise ValueError("Invalid image.")

        score = float(self.model.predict(image))
        score = max(0.0, min(1.0, score))

        return LivenessResult(
            score=score,
            is_live=score >= self.threshold,
            model_name=self.model_name,
            model_version=self.model_version,
        )