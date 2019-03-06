import hashlib
import random
import cpuinfo
import time

from binascii import hexlify, unhexlify
from concurrent.futures import ProcessPoolExecutor
from hashlib import blake2b

from bitarray import bitarray

from .exceptions import InvalidWork
from .util import is_hex

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

if "avx" in _cpu_flags:
    from . import _work_avx as _work
elif "sse4_1" in _cpu_flags:
    from . import _work_sse4_1 as _work
elif "ssse3" in _cpu_flags:  # SSSE3
    from . import _work_ssse3 as _work
elif "sse2" in _cpu_flags:  # SSE2
    from . import _work_sse2 as _work
else:
    from . import _work_ref as _work

WORK_THRESHOLD = int("ffffffc000000000", 16)


__all__ = (
    "WORK_THRESHOLD", "parse_work", "validate_work", "solve_work"
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


def validate_work(block_hash, work, threshold=WORK_THRESHOLD):
    """Validate the proof-of-work.

    :param str block_hash: Block hash as a 64-character hex string
    :param str work: Work as a 16-character hex string
    :param int threshold: The threshold/difficulty for the proof-of-work.
                          NANO network's threshold is used by default.
    :raises InvalidWork: If the work doesn't meet the threshold
    :return: The work as a 16-character hex string
    :rtype: str
    """
    reversed_work = bytearray(unhexlify(work))
    reversed_work.reverse()
    work_hash = bytearray(blake2b(
        b"".join([reversed_work, unhexlify(block_hash)]),
        digest_size=8).digest())
    work_hash.reverse()
    work_value = int(hexlify(work_hash), 16)

    if work_value < threshold:
        raise InvalidWork("Work doesn't meet the required threshold")
    else:
        return work.lower()


def solve_work(block_hash, threshold=WORK_THRESHOLD, timeout=None):
    """Solve the work for the corresponding block hash.

    :param str block_hash: Block hash as a 64-character hex string
    :param int threshold: The threshold/difficulty for the proof-of-work.
                          NANO network's threshold is used by default.
    :param timeout: Timeout in seconds. If provided, None will be returned
                    if the work can't be solved in the given time.
                    If None, the function will block until the work is solved.
    :type timeout: int, float or None
    :return: The solved work as a 64-character hex string or None
             couldn't be solved in time
    :rtype: str or None
    """
    # Reinitialize the random number generator in case this method is being
    # run in a multiprocessing environment; otherwise every process will
    # inherit the same RNG state
    random.seed()

    nonce = random.randint(0, (2**64)-1)
    block_hash_b = unhexlify(block_hash)

    start = time.time()

    while True:
        nonce = _work.do_work(block_hash_b, nonce, threshold)
        work = hexlify(int(nonce).to_bytes(8, byteorder="big"))
        try:
            validate_work(block_hash, work, threshold)
            return str(work, "utf-8")
        except InvalidWork:
            pass

        if timeout and (time.time() - start) > timeout:
            return None
