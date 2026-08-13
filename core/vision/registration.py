from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class RegistrationResult:
    user_id: UUID
    embedding: list[float]
    model_name: str
    model_version: str
    liveness_score: float

class FaceRegistrationService:
    def __init__(
        self,
        preprocessor,
        detector,
        embedding_service,
        liveness_service,
        database,
    ) -> None:
        self.preprocessor = preprocessor
        self.detector = detector
        self.embedding_service = embedding_service
        self.liveness_service = liveness_service
        self.database = database

    async def register(self, user_id: UUID, image: bytes,) -> RegistrationResult:
        decoded = self.preprocessor.decode(image)
        quality = self.preprocessor.validate(decoded)

        if not quality.valid:
            raise ValueError("Image quality is insufficient.")

        detection = self.detector.detect_one(decoded)

        if detection is None:
            raise ValueError("Exactly one face is required.")

        liveness = self.liveness_service.predict(decoded)

        if not liveness.is_live:
            raise ValueError("Liveness verification failed.")

        embedding = self.embedding_service.generate(decoded)

        await self.database.store_embedding(
            user_id=user_id,
            embedding=embedding.vector,
            model_name=embedding.model_name,
            model_version=embedding.model_version,
        )

        return RegistrationResult(
            user_id=user_id,
            embedding=embedding.vector.tolist(),
            model_name=embedding.model_name,
            model_version=embedding.model_version,
            liveness_score=liveness.score,
        )