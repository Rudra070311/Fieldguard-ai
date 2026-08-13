from __future__ import annotations
from typing import Any
from uuid import UUID
import numpy as np
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

class VisionDatabase:
    def __init__(self, session: AsyncSession,) -> None:
        self.session = session

    async def store_embedding(
        self,
        user_id: UUID,
        embedding: np.ndarray,
        model_name: str,
        model_version: str,
    ) -> None:
        values = np.asarray(embedding, dtype=np.float32,).tolist()

        await self.session.execute(
            text(
                """
                INSERT INTO face_embeddings
                (
                    user_id,
                    embedding,
                    model_name,
                    model_version
                )
                VALUES
                (
                    :user_id,
                    :embedding,
                    :model_name,
                    :model_version
                )
                """
            ),
            {
                "user_id": str(user_id),
                "embedding": values,
                "model_name": model_name,
                "model_version": model_version,
            },
        )

        await self.session.flush()

    async def get_embeddings(self, user_id: UUID) -> list[dict[str, Any]]:
        result = await self.session.execute(
            text(
                """
                SELECT
                    embedding,
                    model_name,
                    model_version
                FROM face_embeddings
                WHERE user_id = :user_id
                """
            ),
            {
                "user_id": str(user_id),
            },
        )

        rows = result.mappings().all()

        return [
            {
                "embedding": np.asarray(
                    row["embedding"],
                    dtype=np.float32,
                ),
                "model_name": row["model_name"],
                "model_version": row["model_version"],
            }
            for row in rows
        ]