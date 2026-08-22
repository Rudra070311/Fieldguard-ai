import pytest

VALID_PIN = "482719"
INVALID_FORMAT_PINS = [
    "",
    "12345",
    "1234567",
    "abcdef",
    "12345a",
    "111111",
    "123456",
    "654321",
]

def test_valid_pin_format(pin_verifier):
    pin_verifier.validate_pin_format(VALID_PIN)

@pytest.mark.parametrize("pin", INVALID_FORMAT_PINS)
def test_invalid_pin_format(pin_verifier, pin):
    with pytest.raises(ValueError):
        pin_verifier.validate_pin_format(pin)

@pytest.mark.parametrize(
    "pin",
    ["123456", "654321"],
)
def test_sequential_pin_rejected(pin_verifier, pin):
    with pytest.raises(ValueError):
        pin_verifier.validate_pin_format(pin)

def test_repeated_digit_pin_rejected(pin_verifier):
    with pytest.raises(ValueError):
        pin_verifier.validate_pin_format("111111")

def test_non_string_pin_rejected(pin_verifier):
    with pytest.raises(ValueError):
        pin_verifier.validate_pin_format(123456)

def test_empty_pin_rejected(pin_verifier):
    with pytest.raises(ValueError):
        pin_verifier.validate_pin_format("")

def test_valid_pin_verification(pin_verifier, pin_hasher):
    hashed = pin_hasher.hash(VALID_PIN)
    assert pin_verifier.verify(VALID_PIN, hashed)

def test_invalid_pin_verification(pin_verifier, pin_hasher):
    hashed = pin_hasher.hash(VALID_PIN)
    assert not pin_verifier.verify("482718", hashed)

def test_missing_hash_rejected(pin_verifier):
    assert not pin_verifier.verify(VALID_PIN, "")

def test_missing_pin_rejected(pin_verifier):
    assert not pin_verifier.verify("", "some_hash")