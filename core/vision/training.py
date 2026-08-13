from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional

@dataclass(frozen=True)
class TrainingConfig:
    model_name: str
    model_version: str
    output_path: Path
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 1e-4

@dataclass(frozen=True)
class TrainingResult:
    model_name: str
    model_version: str
    output_path: Path
    samples: int
    epochs: int

class VisionTrainer:
    def __init__(self, model: Any, config: TrainingConfig,) -> None:
        if config.epochs < 1:
            raise ValueError("epochs must be positive.")
        if config.batch_size < 1:
            raise ValueError("batch_size must be positive.")
        if config.learning_rate <= 0:
            raise ValueError("learning_rate must be positive.")

        self.model = model
        self.config = config

    def train(self, samples: Iterable[Any], validation_data: Optional[Iterable[Any]] = None,) -> TrainingResult:
        data = list(samples)

        if not data:
            raise ValueError("Training dataset is empty.")

        self.model.fit(
            data,
            validation_data=validation_data,
            epochs=self.config.epochs,
            batch_size=self.config.batch_size,
            learning_rate=self.config.learning_rate,
        )
        self.config.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.model.save(
            str(self.config.output_path)
        )

        return TrainingResult(
            model_name=self.config.model_name,
            model_version=self.config.model_version,
            output_path=self.config.output_path,
            samples=len(data),
            epochs=self.config.epochs,
        )