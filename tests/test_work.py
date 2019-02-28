from hashlib import blake2b

import pytest

import time

from nanocurrency.work import (
    parse_work, validate_work, solve_work
)
from nanocurrency.exceptions import InvalidWork


VALID_BLOCK_HASH = \
    "B585D9363B8265CFD5993F30A3D6DE6B5CA5CC7879E0AFA94D13F08B713B9FFD"
VALID_WORK = "5b064dcc70b9db0a"


def test_low_threshold_used_for_tests():
    """
    Check that a lower work threshold is used for tests
    """
    from nanocurrency.work import WORK_THRESHOLD

    assert WORK_THRESHOLD < int("ffffffc000000000", 16)


def test_parse_work():
    """
    Test nanocurrency.parse_work
    """
    with pytest.raises(InvalidWork):
        # Work has to be 16 chars long
        parse_work("A"*15)

    with pytest.raises(InvalidWork):
        # Woirk has to be in hex
        parse_work("x"*16)

    # parse_work returns lowercase hex string
    assert parse_work("A"*16) == "a"*16


def test_validate_work():
    with pytest.raises(InvalidWork):
        # Invalid work
        validate_work(block_hash=VALID_BLOCK_HASH, work="e"*16)

    assert validate_work(block_hash=VALID_BLOCK_HASH, work=VALID_WORK)


def test_solve_work():
    fake_hash = blake2b(b"fakeBlock", digest_size=32).hexdigest()

    # Use a very low threshold
    test_threshold = 1028

    result = solve_work(fake_hash, threshold=test_threshold)

    assert validate_work(fake_hash, work=result, threshold=test_threshold)


def test_work_timeout():
    """
    Try solving a work with timeout and make sure it times out
    after the time has passed
    """
    fake_hash = blake2b(b"fakeBlock", digest_size=32).hexdigest()

    start = time.time()

    # Use the maximum possible threshold to make the PoW essentially
    # impossible to solve
    result = solve_work(fake_hash, threshold=(2**64)-1, timeout=0.5)
    end = time.time()

    assert result is None

    # Operation should timeout after 0.5 seconds. Since it's a blocking
    # operation, give it some time to stop
    assert (end - start) > 0.5 and (end - start) < 1
