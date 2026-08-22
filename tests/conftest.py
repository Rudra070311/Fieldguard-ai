from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import pytest
from core.pin.pin_hash import PinHasher
from core.pin.pin_verify import PinVerifier

@pytest.fixture
def settings():
    return SimpleNamespace(
        auth=SimpleNamespace(
            pin_length=6,
            max_failed_attempts=5,
            account_lock_minutes=30,
        ),
        security=SimpleNamespace(
            pin_hash_rounds=12,
        ),
    )

@pytest.fixture
def pin_hasher(settings):
    return PinHasher(settings)

@pytest.fixture
def pin_verifier(settings, pin_hasher):
    return PinVerifier(settings, pin_hasher)

@pytest.fixture
def session():
    return AsyncMock()

@pytest.fixture
def pin_repository():
    repository = MagicMock()
    repository.get_active_by_user = AsyncMock(return_value=None)
    repository.create = AsyncMock()
    repository.get_by_user = AsyncMock(return_value=None)
    repository.update = AsyncMock()
    repository.delete = AsyncMock()
    return repository

@pytest.fixture
def audit_logger():
    logger = MagicMock()
    logger.log_pin_created = MagicMock()
    logger.log_pin_verification = MagicMock()
    logger.log_pin_changed = MagicMock()
    logger.log_pin_revocation = MagicMock()
    return logger

@pytest.fixture
def risk_engine():
    engine = MagicMock()
    engine.update_pin_risk_score = MagicMock()
    return engine