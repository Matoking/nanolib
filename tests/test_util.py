import pytest

from nanolib.util import nbase32_to_bytes, bytes_to_nbase32


def test_nbase32_to_bytes():
    assert nbase32_to_bytes("b6af1a5b") == b'I\x10\xd0 i'


def test_nbase32_to_bytes_empty():
    with pytest.raises(ValueError) as exc:
        nbase32_to_bytes("")

    assert "String is empty" in str(exc.value)


def test_nbase32_to_bytes_invalid():
    with pytest.raises(ValueError) as exc:
        nbase32_to_bytes("1112")

    assert "String is not Nano Base32-encoded" in str(exc.value)


def test_bytes_to_nbase32():
    assert bytes_to_nbase32(b'I\x10\xd0 i') == "b6af1a5b"


def test_bytes_to_nbase32_empty():
    with pytest.raises(ValueError) as exc:
        bytes_to_nbase32(b"")

    assert "Byte array is empty" in str(exc.value)
