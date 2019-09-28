"""
nanolib.util
~~~~~~~~~~~~

Functions for working with the variant of Base32 encoding
(referred to as "Nano Base32") used in account IDs, as well as other general
functions
"""
import nanolib._nbase32

__all__ = (
    "dec_to_hex", "is_hex", "nbase32_to_bytes", "bytes_to_nbase32"
)


def dec_to_hex(d, n):
    return format(d, "0{}X".format(n*2))
    # return "%0.{bytes}X".format(bytes=n*2) % d


def nbase32_to_bytes(nbase32):
    """
    Decode a Nano Base32 encoded string into bytes

    :param str nbase32: Nano Base32 encoded string
    :return: Decoded bytes
    :rtype: bytes
    """
    return nanolib._nbase32.nbase32_to_bytes(bytes(nbase32, "utf-8"))


def bytes_to_nbase32(b):
    """
    Encode bytes to Nano Base32

    :param bytes b: Bytes to encode
    :return: Encoded Nano Base32 string
    :rtype: str
    """
    return nanolib._nbase32.bytes_to_nbase32(b).decode("utf-8")


def is_hex(h):
    try:
        int(h, 16)
        return True
    except ValueError:
        return False
