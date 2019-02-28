from hashlib import blake2b

from ed25519_blake2b import VerifyingKey, SigningKey
from bitarray import bitarray

import binascii
import struct
import array
import random
import sys

__all__ = (
    "hex_to_uint4", "dec_to_hex", "uint_convert_precision",
    "uint4_to_bytes", "bytes_to_uint4", "bytes_to_uint5", "uint4_to_uint5",
    "uint5_to_uint4", "BASE32_LETTERS", "uint5_to_base32", "bytes_to_base32",
    "base32_to_uint5", "hex_to_base32", "is_hex"
)


def hex_to_uint4(h):
    h = "".join(["0" + c for c in h])
    return array.array("B", bytes.fromhex(h))


def dec_to_hex(d, n):
    return format(d, "0{}X".format(n*2))
    # return "%0.{bytes}X".format(bytes=n*2) % d


def uint_convert_precision(uints, source=4, dest=8):
    bits = bitarray()

    for v in uints:
        bits.extend("{{0:0{}b}}".format(source).format(v))

    dest_values = []

    bit_count = len(bits)
    for i in range(0, bit_count, dest):
        if (i+dest) > bit_count:
            continue

        dest_values.append(int(bits[i:i+dest].to01(), 2))

    return dest_values


def uint4_to_bytes(uint4):
    return bytes(uint_convert_precision(uint4, 4, 8))


def bytes_to_uint4(b):
    return uint_convert_precision(b, 8, 4)


def bytes_to_uint5(b):
    return uint_convert_precision(b, 8, 5)


def uint4_to_uint5(uint4):
    return uint_convert_precision(uint4, 4, 5)


def uint5_to_uint4(uint5):
    return uint_convert_precision(uint5, 5, 4)


BASE32_LETTERS = "13456789abcdefghijkmnopqrstuwxyz"


def uint5_to_base32(uint5):
    return "".join([BASE32_LETTERS[u] for u in uint5])


def bytes_to_base32(b):
    uint5 = bytes_to_uint5(b)

    return uint5_to_base32(uint5)


def base32_to_uint5(base32):
    return [BASE32_LETTERS.index(c) for c in base32]


def hex_to_base32(h):
    b = binascii.unhexlify(h)
    return bytes_to_base32(b)


def is_hex(h):
    try:
        int(h, 16)
        return True
    except ValueError:
        return False
