import importlib
import random
import time
from binascii import hexlify, unhexlify
from hashlib import blake2b

import cpuinfo

from .exceptions import InvalidDifficulty, InvalidMultiplier, InvalidWork
from .util import dec_to_hex, is_hex

# Select the PoW C extension depending on highest supported instruction set
# based on the following priorities:
# AVX > SSE4.1 > SSSE3 > SSE2 > reference implementation
#
# This based on a Ryzen 1800X giving the following results:
# avx speed: 6185344 hashes/s (this is likely the fastest on Intel CPUs)
# sse4_1 speed: 6259267 hashes/s
# ssse3 speed: 6249287 hashes/s
# sse2 speed: 4635929 hashes/s
# ref speed: 4539306 hashes/s

# TODO: Maybe run a short benchmark when running solve_work() for the first
#       time?
_cpu_flags = cpuinfo.get_cpu_info()["flags"]
_cpu_flags_by_priority = ("avx", "sse4_1", "ssse3", "sse2", "neon", "ref")

for cpu_flag in _cpu_flags_by_priority:
    if cpu_flag == "ref":
        _work = importlib.import_module("nanolib._work_ref")
        break
    elif cpu_flag in _cpu_flags:
        _work = importlib.import_module(
            "nanolib._work_{}".format(cpu_flag)
        )
        break


WORK_DIFFICULTY = "fffffff800000000"
WORK_DIFFICULTY_INT = int(WORK_DIFFICULTY, 16)


__all__ = (
    "WORK_DIFFICULTY", "parse_work", "validate_work", "validate_difficulty",
    "derive_work_difficulty", "derive_work_multiplier",
    "get_work_value", "solve_work"
)


def parse_work(work):
    """
    Parses a proof-of-work (PoW) value and returns it if it's syntactically
    valid.

    .. note:: This method only checks that the work's format is correct.
              To validate a proof-of-work,
              use :func:`nanolib.work.validate_work`

    :param str work: Work as a 16-character hex string
    :raises InvalidWork: If the work is invalid
    :return: Work as a 16-character hex string
    :rtype: str
    """
    if not len(work) == 16 or not is_hex(work):
        raise InvalidWork("Work has to be a 16-character hexadecimal string")

    # NANO node represents PoW with lowercase hexadecimal letters for some
    # reason. Let's do the same here just to be sure.
    return work.lower()


def get_work_value(block_hash, work, as_hex=False):
    """
    Get the proof-of-work value. The work value must be equal to or higher than
    the work difficulty to be considered valid.

    :param str block_hash: Block hash as a 64-character hex string
    :param str work: Work as a 16-character hex string
    :param bool as_hex: Whether to return the work value as a hex string or an
                        integer.
                        If True, a 16-character hex string is returned.
                        If False, a 64-bit integer is returned.
                        A 64-bit integer is returned by default.
    :raises InvalidWork: If the work isn't a 16-character hex string
    :raises InvalidBlockHash: If the block hash isn't a 64-character hex string
    :return: A 16-character hex string or a 64-bit integer depending on
             `as_hex`
    :rtype: int or str
    """
    # Import is deferred to avoid a circular import
    from nanolib.blocks import validate_block_hash

    validate_block_hash(block_hash)
    parse_work(work)

    reversed_work = bytearray(unhexlify(work))
    reversed_work.reverse()
    work_hash = bytearray(blake2b(
        b"".join([reversed_work, unhexlify(block_hash)]),
        digest_size=8).digest())
    work_hash.reverse()
    work_value = int(hexlify(work_hash), 16)

    if as_hex:
        work_value = dec_to_hex(work_value, 8).lower()

    return work_value


def validate_work(block_hash, work, difficulty=WORK_DIFFICULTY):
    """Validate the proof-of-work.

    :param str block_hash: Block hash as a 64-character hex string
    :param str work: Work as a 16-character hex string
    :param str difficulty: The difficulty for the proof-of-work
                           as a 16-character hex string.
                           NANO network's difficulty is used by default.
    :raises InvalidWork: If the work doesn't meet the difficulty or isn't
                         a 16-character hex string
    :return: The work as a 16-character hex string
    :rtype: str
    """
    difficulty = parse_difficulty(difficulty)

    work_value = get_work_value(block_hash=block_hash, work=work)

    if work_value < difficulty:
        raise InvalidWork("Work doesn't meet the required difficulty")

    return work.lower()


def validate_difficulty(difficulty):
    """Validate the work difficulty.

    :param str difficulty: Work difficulty as a 16-character hex string
    :raises InvalidDifficulty: If the difficulty isn't a 16-character hex value
    :return: The work difficulty as a 16-character hex string
    :rtype: str
    """
    if not len(difficulty) == 16 or not is_hex(difficulty):
        raise InvalidDifficulty(
            "Threshold has to be a 16-character hex string"
        )

    return difficulty.lower()


def parse_difficulty(difficulty):
    """Parse and return given hex-formatted difficulty as an integer.

    :param str difficulty: Work difficulty as a 16-character hex string
    :raises InvalidDifficulty: If the difficulty isn't a 16-character hex
                               string
    :return: The work difficulty as an integer
    :rtype: int
    """
    if is_hex(difficulty) and len(difficulty) == 16:
        return int(difficulty, 16)

    raise InvalidDifficulty("Difficulty has to be a 16-character hex string")


def derive_work_difficulty(multiplier, base_difficulty=None):
    """Derive the work difficulty from a provided multiplier
    and a base difficulty

    :param float multiplier: Work multiplier as a float. Work difficulty with
                             a multiplier of 2 requires on average twice as
                             much work compared to the base difficulty.
    :param str base_difficulty: Base difficulty as a 16-character hex string.
                                NANO network's difficulty is used by default.
    :raises InvalidDifficulty: If the difficulty isn't a 16-character hex
                               string
    :raises ValueError: If the resulting difficulty is larger than \
                        :math:`2^{64}-1`
    :return: The adjusted work difficulty as a 16-character hex string
    :rtype: str
    """
    if base_difficulty is None:
        base_difficulty = WORK_DIFFICULTY_INT
    else:
        base_difficulty = parse_difficulty(base_difficulty)

    try:
        multiplier = float(multiplier)
    except ValueError:
        raise InvalidMultiplier("Multiplier is not a float")

    if multiplier <= 0:
        raise InvalidMultiplier(
            "Multiplier has to be a positive non-zero float")

    difficulty = int((base_difficulty - (1 << 64)) / multiplier + (1 << 64))

    if difficulty > (2**64)-1:
        raise ValueError("Resulting difficulty is too large")

    return dec_to_hex(difficulty, 8).lower()


def derive_work_multiplier(difficulty, base_difficulty=None):
    """Derive the work multiplier from a difficulty and a base difficulty.

    :param str difficulty: Work difficulty as a 16-character hex string
    :param str base_difficulty: Base work difficulty as a 16-character hex
                                string.
                                NANO network's difficulty is used by default.
    :raises InvalidDifficulty: If difficulty isn't a 16-character hex string
    :return: The work multiplier as a float. Work difficulty with a multiplier
             of 2 requires on average twice as much work compared to the base
             difficulty.
    :rtype: float
    """
    if base_difficulty is None:
        base_difficulty = WORK_DIFFICULTY_INT
    else:
        base_difficulty = parse_difficulty(base_difficulty)

    difficulty = parse_difficulty(difficulty)

    multiplier = \
        float((1 << 64) - base_difficulty) / float((1 << 64) - difficulty)
    return multiplier


def solve_work(block_hash, difficulty=WORK_DIFFICULTY, timeout=None):
    """Solve the work for the corresponding block hash.

    :param str block_hash: Block hash as a 64-character hex string
    :param str difficulty: The difficulty for the proof-of-work as a
                           16-character hex string.
                           NANO network's difficulty is used by default.
    :param timeout: Timeout in seconds. If provided, None will be returned
                    if the work can't be solved in the given time.
                    If None, the function will block until the work is solved.
    :type timeout: int, float or None
    :return: The solved work as a 64-character hex string or None
             couldn't be solved in time
    :rtype: str or None
    """
    validate_difficulty(difficulty)

    # Reinitialize the random number generator in case this method is being
    # run in a multiprocessing environment; otherwise every process will
    # inherit the same RNG state
    random.seed()

    nonce = random.randint(0, (2**64)-1)
    block_hash_b = unhexlify(block_hash)

    start = time.time()

    while True:
        nonce = _work.do_work(
            block_hash_b, nonce, parse_difficulty(difficulty))
        work = hexlify(int(nonce).to_bytes(8, byteorder="big"))
        try:
            validate_work(block_hash, work, difficulty)
            return str(work, "utf-8")
        except InvalidWork:
            pass

        if timeout and (time.time() - start) > timeout:
            return None
