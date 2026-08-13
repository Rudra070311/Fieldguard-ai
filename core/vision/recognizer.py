from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass(frozen=True)
class RecognitionResult:
    matched: bool
    score: float
    threshold: float

class FaceRecognizer:
    def __init__(self, threshold: float = 0.75,) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Invalid recognition threshold.")

        self.threshold = threshold

    @staticmethod
    def similarity(first: np.ndarray, second: np.ndarray,) -> float:
        first = np.asarray(first, dtype=np.float32).reshape(-1)
        second = np.asarray(second, dtype=np.float32).reshape(-1)

        if first.size == 0 or second.size == 0:
            raise ValueError("Embeddings cannot be empty.")
        if first.shape != second.shape:
            raise ValueError("Embedding dimensions do not match.")

        first_norm = np.linalg.norm(first)
        second_norm = np.linalg.norm(second)

        if first_norm <= 0.0 or second_norm <= 0.0:
            raise ValueError("Invalid zero embedding.")

        score = float(np.dot(first, second) / (first_norm * second_norm))

        return max(0.0, min(1.0, (score + 1.0) / 2.0))

    def compare(self, probe: np.ndarray, reference: np.ndarray,) -> RecognitionResult:
        score = self.similarity(probe, reference)

        return RecognitionResult(
            matched=score >= self.threshold,
            score=score,
            threshold=self.threshold,
        )

    def identify(self, probe: np.ndarray, references: dict[str, np.ndarray],) -> Optional[tuple[str, RecognitionResult]]:
        best_id: Optional[str] = None
        best_result: Optional[RecognitionResult] = None

        for identity, reference in references.items():
            result = self.compare(probe, reference)

            if (best_result is None or result.score > best_result.score):
                best_id = identity
                best_result = result

        if best_id is None or best_result is None:
            return None
        if not best_result.matched:
            return None

        return best_id, best_result