
import pytest

import json

from tests.data import BLOCKS

from nanolib.blocks import Block, MAX_BALANCE
from nanolib.exceptions import (
    InvalidAccount, InvalidBlock, InvalidSignature, InvalidWork,
    InvalidBlockHash, InvalidBalance, InvalidPublicKey)


VALID_ACCOUNT_ID = \
    "xrb_1took1orwwfohx7qf13pju7144o8d4qzxizx14pua7cxsuinxzjbb6goarud"
VALID_ACCOUNT_PUBLIC_KEY = \
    "6AB5902B8E71B57F4B7680368ECA010AA658AFFEC3FD00ADB4155DCEE14EFE29"

TEST_BLOCKS = []

for name in BLOCKS.keys():
    TEST_BLOCKS.append((name, BLOCKS[name]))


@pytest.mark.parametrize("name,block", TEST_BLOCKS)
def test_block_hash(name, block):
    """
    Calculate block hash for every test block and check that they match
    with the test data
    """
    correct_block_hash = block["hash"]
    block = Block.from_dict(block["data"])

    assert block.block_hash == correct_block_hash


@pytest.mark.parametrize("name,block", TEST_BLOCKS)
def test_block_json(name, block):
    """
    Deserialize every block from JSON and ensure they can be serialized
    back into identical JSON
    """
    test_block = block["data"]
    block = Block.from_json(json.dumps(test_block))

    assert json.loads(block.json()) == test_block


@pytest.mark.parametrize("name,block", TEST_BLOCKS)
def test_block_complete(name, block):
    """
    Deserialize every block from JSON and check that they have valid PoW and
    signatures
    """
    test_block = block["data"]
    block = Block.from_json(json.dumps(test_block))

    assert block.has_valid_work

    if block.account:
        assert block.has_valid_signature
        assert block.complete
    else:
        # Nano reference wallet's RPC API doesn't return some legacy blocks
        # with 'account' fields set even if they're required to verify the
        # signature.
        try:
            assert not block.account
            block.verify_signature()
        except ValueError as e:
            assert "'account' not included" in str(e)
            assert not block.complete


BLOCKS_AND_TYPES = (
    (BLOCKS["open"], "open"),
    (BLOCKS["send"], "send"),
    (BLOCKS["receive"], "receive"),
    (BLOCKS["change"], "change"),
    (BLOCKS["state_sendreceive"], "send/receive"),
    (BLOCKS["state_sendreceive2"], "send/receive"),
    (BLOCKS["state_change"], "change"),
    (BLOCKS["state_epoch"], "epoch"),
)


def test_block_tx_type():
    """
    Load different blocks and check that their tx_types match
    """
    for block_data, tx_type in BLOCKS_AND_TYPES:
        block = Block.from_dict(block_data["data"])
        assert block.tx_type == tx_type, \
            "For block %s, expected tx_type %s, got %s" % (
                block_data["hash"], tx_type, block.tx_type)


def test_block_invalid_block_type():
    """
    Try creating a block with an invalid block type
    """
    with pytest.raises(ValueError) as exc:
        Block(block_type="transactionate_funds")

    assert "block_type" in str(exc)


def test_block_invalid_signature():
    """
    Try to load a block with invalid signature
    """
    # 'open' blocks are the only legacy blocks that can be verified as-is
    # Other blocks need to add the optional 'account' parameter
    block = BLOCKS["open"]["data"].copy()
    block["signature"] = "B"*128

    with pytest.raises(InvalidSignature) as exc:
        # Invalid signature (can't be verified)
        Block.from_dict(block)

    assert "couldn't be verified" in str(exc)

    block["signature"] = "A"

    with pytest.raises(InvalidSignature) as exc:
        # Invalid signature (incorrect length)
        Block.from_dict(block)

    assert "hexadecimal string" in str(exc)


def test_block_signature_with_missing_parameters():
    """
    Try to verify a signature for a block that's missing the 'account' or
    'signature' parameters

    NANO's rai_node API returns JSON representations of blocks that may not
    contain the 'account' parameter
    """
    block = Block.from_dict(BLOCKS["receive"]["data"])

    with pytest.raises(ValueError):
        # Missing account
        block.verify_signature()

    block.signature = None
    block.account = BLOCKS["receive"]["account"]

    with pytest.raises(ValueError):
        # Missing signature
        block.verify_signature()

    # Add the missing parameters
    block.account = BLOCKS["receive"]["account"]
    block.signature = BLOCKS["receive"]["data"]["signature"]

    block.verify_signature()

    # Invalid signature won't cause an exception with 'has_valid_signature'
    block.signature = "1"*128
    assert not block.has_valid_signature


def test_block_sign():
    """
    Sign a block and verify it
    """
    private_key = \
        "587d4d70c1a3b66db89ad0e69e12bbd06774e8a161d2dca0c0c734556b8656ad"
    account_id = \
        "xrb_3f3iy4xh3umniqzpisrbuj6s1scde3mj83ffwgr4ckq1q6oirez1yjwq9t3y"

    block = Block(
        block_type="state",
        account=account_id,
        representative=account_id,
        previous=None,
        balance=100000,
        link="A4647CEBA216FD004AAFE3F552BA98739E6C4AD75A8C3E6A12B93531725D9F3A")

    assert not block.has_valid_signature

    block.sign(private_key)
    assert block.has_valid_signature

    with pytest.raises(ValueError):
        # Can't sign again if the block already has a signature
        block.sign(private_key)


def test_block_invalid_work(block_factory):
    """
    Try to load a block with invalid work
    """
    block_data = BLOCKS["receive"]["data"].copy()
    block_data["work"] = "a"*16

    with pytest.raises(InvalidWork):
        Block.from_dict(block_data)


def test_block_solve_work(block_factory):
    """
    Solve PoW for a work and verify it
    """
    block = block_factory("send")
    block.work = None

    assert not block.has_valid_work

    block.solve_work()
    assert block.has_valid_work

    with pytest.raises(ValueError):
        # Block already has a valid PoW
        block.solve_work()

    block.work = None

    # Try solving PoW with essentially impossible threshold
    assert not block.solve_work(threshold=(2**64)-1, timeout=0.1)


def test_block_verify_work(block_factory):
    """
    Load a block with work, and verify once with work and once without
    """
    block = block_factory("send")

    block.verify_work()

    with pytest.raises(InvalidWork):
        # Work doesn't meet the threshold
        block.work = "a"*16
        block.verify_work()

    with pytest.raises(ValueError):
        # Missing work
        block.work = None
        block.verify_work()

    # 'has_valid_work' won't cause an exception
    block.work = "a"*16
    assert not block.has_valid_work


def test_block_verify_work_threshold(block_factory):
    """
    Load a block with work, and verify it different work thresholds
    making it either pass or fail
    """
    block = block_factory("send")

    # Passes with normal threshold
    block.verify_work()

    with pytest.raises(InvalidWork):
        # Insufficient work for this threshold
        block.verify_work(threshold=18446744068091581575)

    # Threshold can also be changed using the 'threshold' parameter
    block.threshold = 18446744068091581575

    with pytest.raises(InvalidWork):
        block.verify_work()

    block.threshold = 18446744068091581574


def test_block_invalid_threshold():
    """
    Create a Block with different thresholds to make it either pass or fail
    """
    block_data = BLOCKS["send"]["data"].copy()

    with pytest.raises(InvalidWork):
        Block.from_dict(block_data, threshold=18446744068091581575)

    block = Block.from_dict(block_data, threshold=18446744068091581574)

    # Threshold is required
    with pytest.raises(ValueError):
        block.threshold = None


def test_block_work_value(block_factory):
    """
    Read the work value from the block
    """
    block = block_factory("send")

    assert block.work_value == 18446744068091581574

    block.work = None
    assert not block.work_value


def test_block_skip_verify():
    """
    Deserialize a Block by skipping the verification of signature and PoW
    """
    block_data = BLOCKS["receive"]["data"].copy()
    block_data["work"] = "a"*16

    # The work is invalid, but it's OK
    Block.from_dict(block_data, verify=False)
    Block.from_json(json.dumps(block_data), verify=False)

    block_data["signature"] = "A"*128

    # The signature is invalid, but that's OK as well now
    Block.from_dict(block_data, verify=False)
    Block.from_json(json.dumps(block_data), verify=False)


def test_block_set_account(block_factory):
    """
    Test changing the 'account' block attribute
    """
    block = block_factory("receive")

    block.signature = None
    block.account = VALID_ACCOUNT_ID

    with pytest.raises(InvalidAccount):
        block.account = "invalid"


def test_block_set_source(block_factory):
    """
    Test changing the 'source' block attribute
    """
    block = block_factory("open")

    block.signature = None
    block.source = "A"*64

    with pytest.raises(InvalidBlockHash):
        block.source = "A"*65


def test_block_set_previous(block_factory):
    """
    Test changing the 'previous' block attribute
    """
    block = block_factory("send")

    block.signature = None
    block.previous = "A"*64

    with pytest.raises(InvalidPublicKey):
        block.previous = "A"*65


def test_block_set_destination(block_factory):
    """
    Test changing the 'destination' block attribute
    """
    block = block_factory("send")

    block.signature = None
    block.destination = VALID_ACCOUNT_ID

    with pytest.raises(InvalidAccount):
        block.destination = "invalid"


def test_block_set_representative(block_factory):
    """
    Test changing the 'representative' block attribute
    """
    block = block_factory("open")

    block.signature = None
    block.representative = VALID_ACCOUNT_ID

    with pytest.raises(InvalidAccount):
        block.destination = "invalid"


def test_block_set_balance(block_factory):
    """
    Test changing the 'balance' block attribute
    """
    # Hex-formatted balance
    block = block_factory("send")

    block.signature = None
    block.balance = 100

    assert json.loads(block.json())["balance"] == \
        "00000000000000000000000000000064"

    with pytest.raises(InvalidBalance):
        # Pre-state blocks only accept hex balances when deserializing
        # from a dict
        block_data = BLOCKS["send"]["data"].copy()
        block_data["balance"] = str(2**128)

        Block.from_dict(block_data)

    # String-formatted balance
    block = block_factory("state_sendreceive")

    block.signature = None
    block.balance = 100

    assert json.loads(block.json())["balance"] == "100"

    # Invalid balances
    with pytest.raises(InvalidBalance):
        block.balance = -1

    with pytest.raises(InvalidBalance):
        block.balance = MAX_BALANCE + 1


def test_block_legacy_send_from_dict():
    """
    When deserializing a legacy send block, the balance has to be hex-formatted
    """
    block_data = BLOCKS["send"]["data"].copy()
    block_data["balance"] = "10000000"

    with pytest.raises(InvalidBalance) as exc:
        Block.from_dict(block_data)

    assert "needs to be a hex" in str(exc)


def test_block_set_link(block_factory):
    """
    Test changing the 'link' block attribute which will also change
    'link_as_account'
    """
    block = block_factory("state_sendreceive")

    block.signature = None
    block.link = VALID_ACCOUNT_PUBLIC_KEY

    assert block.link == VALID_ACCOUNT_PUBLIC_KEY
    assert block.link_as_account == VALID_ACCOUNT_ID

    with pytest.raises(InvalidBlockHash):
        # Block hash in't hex
        block.link = "G"*64

    # None defaults to all-zeroes public key
    block.link = None

    assert block.link == "0" * 64
    assert block.link_as_account == \
        "xrb_1111111111111111111111111111111111111111111111111111hifc8npp"


def test_block_set_link_as_address(block_factory):
    """
    Test changing the 'link_as_account' block attribute which will also change
    'link'
    """
    block = block_factory("state_sendreceive")

    block.signature = None
    block.link_as_account = VALID_ACCOUNT_ID

    assert block.link_as_account == VALID_ACCOUNT_ID
    assert block.link == VALID_ACCOUNT_PUBLIC_KEY

    with pytest.raises(InvalidAccount):
        # 'link_as_account' isn't an account ID
        block.link_as_account = "invalid"

    # None defaults to all-zeroes public key
    block.link_as_account = None

    assert block.link == "0" * 64
    assert block.link_as_account == \
        "xrb_1111111111111111111111111111111111111111111111111111hifc8npp"


def test_block_missing_parameters():
    """
    Try to load a block with a missing required parameter
    """
    block_data = BLOCKS["receive"]["data"].copy()
    del block_data["previous"]

    with pytest.raises(InvalidBlock) as exc:
        Block.from_dict(block_data)

    assert "is missing required parameters: previous" in str(exc)


def test_block_prohibited_parameters():
    """
    Try to load a block with an additional prohibited parameter
    """
    block_data = BLOCKS["change"]["data"].copy()
    block_data["balance"] = "10000"

    with pytest.raises(InvalidBlock) as exc:
        Block.from_dict(block_data)

    assert "has prohibited parameters: balance" in str(exc)


def test_block_is_complete():
    """
    Check if a block is complete using Block.is_complete
    """
    block = Block.from_dict(BLOCKS["receive"]["data"])

    assert not block.complete

    # Add the 'account', so that the block can be verified
    block.account = BLOCKS["receive"]["account"]

    assert block.complete
