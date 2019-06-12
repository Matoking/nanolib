import pytest

from nanolib.blocks import Block

from tests.data import BLOCKS


@pytest.fixture(autouse=True)
def low_pow_difficulty(monkeypatch):
    # Use a far lower default difficulty for unit tests
    TEST_DIFFICULTY = "8345468f269004a2"
    monkeypatch.setattr("nanolib.blocks.WORK_DIFFICULTY", TEST_DIFFICULTY)
    monkeypatch.setattr("nanolib.work.WORK_DIFFICULTY", TEST_DIFFICULTY)
    monkeypatch.setattr("nanolib.WORK_DIFFICULTY", TEST_DIFFICULTY)


@pytest.fixture(scope="function")
def block_factory():
    def _create_func(name):
        return Block.from_dict(BLOCKS[name]["data"])

    return _create_func
