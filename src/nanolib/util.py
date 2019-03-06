from bitarray import bitarray

__all__ = (
    "dec_to_hex", "is_hex", "nbase32_to_bytes", "bytes_to_nbase32"
)


def dec_to_hex(d, n):
    return format(d, "0{}X".format(n*2))
    # return "%0.{bytes}X".format(bytes=n*2) % d


NBASE32_LETTERS = b'13456789abcdefghijkmnopqrstuwxyz'
NBASE32_TABLE = {}
NBASE32_REVERSE_TABLE = {}

for i, c in enumerate(NBASE32_LETTERS):
    NBASE32_TABLE[c] = bitarray(format(i, "05b"))
    NBASE32_REVERSE_TABLE[i] = str(bytes([c]), "utf-8")


def nbase32_to_bytes(nbase32):
    nbase32 = bytes(nbase32, "utf-8")
    bits = bitarray()
    for c in nbase32:
        bits.extend(NBASE32_TABLE[c])

    leftover = len(bits) % 8

    if leftover:
        # Truncate to a multiple of 8 bits if necessary
        bits = bits[leftover:]

    return bits.tobytes()


PADDING = bitarray([0, 0, 0])


def bytes_to_nbase32(b):
    bits = bitarray()
    if isinstance(b, bytearray):
        b = bytes(b)
    bits.frombytes(b)

    leftover = len(bits) % 5

    if leftover != 0:
        # Zero-pad the bitarray to a multiple of 5 bits if necessary
        bits = bitarray([0]*(5 - (leftover))) + bits

    output = []

    for i in range(0, len(bits), 5):
        # Right shift each 8-bit int to get the intended 5-bit value
        output.append(bits[i:i+5].tobytes()[0] >> 3)

    return "".join([
        NBASE32_REVERSE_TABLE[i] for i in output
    ])


def is_hex(h):
    try:
        int(h, 16)
        return True
    except ValueError:
        return False
