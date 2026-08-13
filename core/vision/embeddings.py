from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass(frozen=True)
class EmbeddingResult:
    vector: np.ndarray
    model_name: str
    model_version: str
    dimension: int

class FaceEmbeddingService:
    def __init__(
        self,
        model: Any,
        model_name: str,
        model_version: str,
    ) -> None:
        self.model = model
        self.model_name = model_name
        self.model_version = model_version

    def generate(self, image: np.ndarray,) -> EmbeddingResult:
        if image is None or image.size == 0:
            raise ValueError("Invalid image.")

        embedding = self.model.get(image)
        vector = np.asarray(
            embedding,
            dtype=np.float32,
        ).reshape(-1)

        if vector.size == 0:
            raise ValueError("Embedding generation failed.")

        norm = np.linalg.norm(vector)

        if norm <= 0.0:
            raise ValueError("Invalid zero embedding.")

        vector = vector / norm

        return EmbeddingResult(
            vector=vector,
            model_name=self.model_name,
            model_version=self.model_version,
            dimension=int(vector.size),
        )

    @staticmethod
    def serialize(vector: np.ndarray) -> list[float]:
        vector = np.asarray(vector, dtype=np.float32)

        if vector.ndim != 1:
            raise ValueError("Embedding must be one-dimensional.")

        return vector.tolist()

    @staticmethod
    def deserialize(values: list[float]) -> np.ndarray:
        vector = np.asarray(values, dtype=np.float32)

        if vector.ndim != 1 or vector.size == 0:
            raise ValueError("Invalid embedding.")

        norm = np.linalg.norm(vector)

        if norm <= 0.0:
            raise ValueError("Invalid zero embedding.")

        return vector / norm