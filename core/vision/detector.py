from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import numpy as np

@dataclass(frozen=True)
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def area(self) -> float:
        return self.width * self.height

@dataclass(frozen=True)
class FaceDetection:
    bbox: BoundingBox
    confidence: float
    landmarks: Optional[np.ndarray] = None

class FaceDetector:
    def __init__(self, model: Any, confidence_threshold: float = 0.60, max_faces: int = 1,) -> None:
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError("Invalid confidence threshold.")

        if max_faces < 1:
            raise ValueError("max_faces must be positive.")

        self.model = model
        self.confidence_threshold = confidence_threshold
        self.max_faces = max_faces

    def detect(self, image: np.ndarray) -> list[FaceDetection]:
        if image is None or image.size == 0:
            raise ValueError("Invalid image.")

        results = self.model.get(image)
        detections: list[FaceDetection] = []

        for face in results:
            confidence = float(getattr(face, "det_score", 0.0))
            if confidence < self.confidence_threshold:
                continue

            bbox_data = np.asarray(face.bbox, dtype=np.float32)

            if bbox_data.shape != (4,):
                continue

            landmarks = getattr(face, "kps", None)
            detections.append(
                FaceDetection(
                    bbox=BoundingBox(
                        x1=float(bbox_data[0]),
                        y1=float(bbox_data[1]),
                        x2=float(bbox_data[2]),
                        y2=float(bbox_data[3]),
                    ),
                    confidence=confidence,
                    landmarks=(
                        np.asarray(landmarks, dtype=np.float32)
                        if landmarks is not None
                        else None
                    ),
                )
            )

        detections.sort(
            key=lambda item: item.confidence,
            reverse=True,
        )

        return detections[: self.max_faces]

    def detect_one(self, image: np.ndarray,) -> Optional[FaceDetection]:
        detections = self.detect(image)

        if len(detections) != 1:
            return None

        return detections[0]