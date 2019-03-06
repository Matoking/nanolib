import pytest

from nanolib.blocks import Block

from tests.data import BLOCKS


@pytest.fixture(autouse=True)
def low_pow_threshold(monkeypatch):
    # Use a far lower default threshold for unit tests
    TEST_THRESHOLD = 9459044173002835106
    monkeypatch.setattr("nanolib.blocks.WORK_THRESHOLD", TEST_THRESHOLD)
    monkeypatch.setattr("nanolib.work.WORK_THRESHOLD", TEST_THRESHOLD)
    monkeypatch.setattr("nanolib.WORK_THRESHOLD", TEST_THRESHOLD)


@pytest.fixture(scope="function")
def block_factory():
    def _create_func(name):
        return Block.from_dict(BLOCKS[name]["data"])

    return _create_func
