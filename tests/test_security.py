from __future__ import annotations
import pytest
from cryptography.fernet import Fernet
from config.settings import Settings
from core.security.constant_time import safe_compare
from core.security.encryption_manager import EncryptionManager
from core.security.hash_manager import HashManager
from core.security.password_manager import PasswordManager
from core.security.token_hash import TokenHashManager

def test_safe_compare_equal_values():
    assert safe_compare("secret-value", "secret-value") is True

def test_safe_compare_different_values():
    assert safe_compare("secret-value", "different-value") is False

@pytest.mark.parametrize("value", [None, 123, b"secret"])
def test_safe_compare_rejects_non_strings(value):
    assert safe_compare(value, "secret") is False

def test_hash_manager_hashes_value():
    manager = HashManager()
    hashed = manager.hash("test-password")

    assert isinstance(hashed, str)
    assert hashed != "test-password"
    assert hashed.startswith("$argon2")

def test_hash_manager_verifies_correct_value():
    manager = HashManager()
    hashed = manager.hash("test-password")

    assert manager.verify(hashed, "test-password") is True

def test_hash_manager_rejects_wrong_value():
    manager = HashManager()
    hashed = manager.hash("test-password")

    assert manager.verify(hashed, "wrong-password") is False

def test_hash_manager_rejects_empty_value():
    manager = HashManager()

    with pytest.raises(ValueError):
        manager.hash("")

def test_hash_manager_invalid_hash_returns_false():
    manager = HashManager()

    assert manager.verify("not-a-valid-hash", "password") is False

def test_hash_manager_needs_rehash_invalid_hash():
    manager = HashManager()

    assert manager.needs_rehash("invalid-hash") is True

def test_token_generation():
    token = TokenHashManager.generate()

    assert isinstance(token, str)
    assert len(token) > 0

def test_token_generation_rejects_short_length():
    with pytest.raises(ValueError):
        TokenHashManager.generate(31)

def test_token_generation_produces_unique_tokens():
    tokens = {TokenHashManager.generate() for _ in range(100)}

    assert len(tokens) == 100

def test_token_hashing_is_deterministic():
    token = "test-secure-token"
    first = TokenHashManager.hash(token)
    second = TokenHashManager.hash(token)

    assert first == second
    assert len(first) == 64

def test_token_hash_rejects_empty_token():
    with pytest.raises(ValueError):
        TokenHashManager.hash("")

def test_token_verification():
    token = TokenHashManager.generate()
    token_hash = TokenHashManager.hash(token)

    assert TokenHashManager.verify(token, token_hash) is True

def test_token_verification_rejects_wrong_token():
    token = TokenHashManager.generate()
    token_hash = TokenHashManager.hash(token)

    assert TokenHashManager.verify("wrong-token", token_hash) is False

def test_token_verification_rejects_missing_values():
    assert TokenHashManager.verify("", "hash") is False
    assert TokenHashManager.verify("token", "") is False

def test_password_generation():
    password = PasswordManager.generate()

    assert isinstance(password, str)
    assert len(password) > 0

def test_password_generation_rejects_short_length():
    with pytest.raises(ValueError):
        PasswordManager.generate(7)

def test_password_generation_produces_unique_passwords():
    passwords = {PasswordManager.generate() for _ in range(100)}

    assert len(passwords) == 100

def test_password_hash_and_verify():
    manager = PasswordManager()
    password = "Strong-test-password-123!"
    password_hash = manager.hash(password)

    assert manager.verify(password, password_hash) is True

def test_password_rejects_wrong_password():
    manager = PasswordManager()
    password_hash = manager.hash("correct-password")

    assert manager.verify("wrong-password", password_hash) is False

def test_password_hash_rejects_empty_password():
    manager = PasswordManager()

    with pytest.raises(ValueError):
        manager.hash("")

def test_password_verify_rejects_missing_values():
    manager = PasswordManager()
    password_hash = manager.hash("correct-password")

    assert manager.verify("", password_hash) is False
    assert manager.verify("correct-password", "") is False

def make_test_settings() -> Settings:
    key = Fernet.generate_key().decode("utf-8")

    return Settings(
        database={"url": "postgresql://test:test@localhost/test"},
        security={"jwt_secret": "test-jwt-secret", "encryption_key": key}
    )

def test_encryption_manager_encrypts_value():
    manager = EncryptionManager(make_test_settings())
    encrypted = manager.encrypt("secret message")

    assert isinstance(encrypted, str)
    assert encrypted != "secret message"

def test_encryption_manager_decrypts_value():
    manager = EncryptionManager(make_test_settings())
    original = "secret message"
    encrypted = manager.encrypt(original)

    assert manager.decrypt(encrypted) == original

def test_encryption_produces_different_ciphertext():
    manager = EncryptionManager(make_test_settings())
    first = manager.encrypt("same message")
    second = manager.encrypt("same message")

    assert first != second

def test_encryption_rejects_empty_value():
    manager = EncryptionManager(make_test_settings())

    with pytest.raises(ValueError):
        manager.encrypt("")

def test_decryption_rejects_invalid_ciphertext():
    manager = EncryptionManager(make_test_settings())

    with pytest.raises(ValueError):
        manager.decrypt("invalid-encrypted-value")

def test_encryption_manager_rejects_invalid_key():
    settings = Settings(
        database={"url": "postgresql://test:test@localhost/test"},
        security={"jwt_secret": "test-jwt-secret", "encryption_key": "invalid-key"}
    )

    with pytest.raises(ValueError):
        EncryptionManager(settings)