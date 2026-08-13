from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import cv2
import numpy as np

@dataclass(frozen=True)
class ImageQuality:
    width: int
    height: int
    brightness: float
    blur_score: float
    valid: bool

class ImagePreprocessor:
    def __init__(
        self,
        min_width: int = 160,
        min_height: int = 160,
        target_size: int = 224,
        min_brightness: float = 20.0,
        max_brightness: float = 235.0,
        min_blur_score: float = 25.0,
    ) -> None:
        self.min_width = min_width
        self.min_height = min_height
        self.target_size = target_size
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.min_blur_score = min_blur_score

    def decode(self, image: bytes) -> np.ndarray:
        if not image:
            raise ValueError("Image data cannot be empty.")

        array = np.frombuffer(image, dtype=np.uint8)
        decoded = cv2.imdecode(array, cv2.IMREAD_COLOR)

        if decoded is None:
            raise ValueError("Invalid image data.")

        return decoded

    def validate(self, image: np.ndarray) -> ImageQuality:
        if image is None or image.size == 0:
            raise ValueError("Invalid image.")

        height, width = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        valid = (
            width >= self.min_width
            and height >= self.min_height
            and self.min_brightness <= brightness <= self.max_brightness
            and blur_score >= self.min_blur_score
        )

        return ImageQuality(
            width=width,
            height=height,
            brightness=brightness,
            blur_score=blur_score,
            valid=valid,
        )

    def resize(self, image: np.ndarray) -> np.ndarray:
        return cv2.resize(
            image,
            (self.target_size, self.target_size),
            interpolation=cv2.INTER_AREA,
        )

    def normalize(self, image: np.ndarray) -> np.ndarray:
        image = image.astype(np.float32) / 255.0
        return (image - 0.5) / 0.5

    def preprocess(self, image: bytes) -> np.ndarray:
        decoded = self.decode(image)
        quality = self.validate(decoded)

        if not quality.valid:
            raise ValueError("Image quality is insufficient.")

        resized = self.resize(decoded)
        return self.normalize(resized)