import pytest

from nanolib.exceptions import (
    InvalidSeed, InvalidPrivateKey, InvalidPublicKey, InvalidAccount)
from nanolib.accounts import (
    AccountIDPrefix, get_account_key_pair, get_account_id,
    get_account_public_key, generate_account_private_key,
    generate_account_key_pair, generate_account_id, generate_seed,
    is_account_id_valid
)
from nanolib.util import is_hex


SEED = "bba817a4fa1418e10d014c99055c4922afa0f84b324e7850baf4b3b8b6af1a5b"
FIRST_PRIVATE_KEY = "64e0752579d3e6a6ea4f60b6596ff62cd59fc3160a687fe999522121d0a73c06"
FIRST_PUBLIC_KEY = "6ab5902b8e71b57f4b7680368eca010aa658affec3fd00adb4155dcee14efe29"
FIRST_ACCOUNT_ID_XRB = "xrb_1took1orwwfohx7qf13pju7144o8d4qzxizx14pua7cxsuinxzjbb6goarud"
FIRST_ACCOUNT_ID_NANO = "nano_1took1orwwfohx7qf13pju7144o8d4qzxizx14pua7cxsuinxzjbb6goarud"


def test_get_account_key_pair():
    with pytest.raises(InvalidPrivateKey):
        # Private key isn't 64 chars long
        get_account_key_pair("A"*63)

    with pytest.raises(InvalidPrivateKey):
        # Private key isn't in hex
        get_account_key_pair("G"*64)

    kp = get_account_key_pair(FIRST_PRIVATE_KEY)

    assert kp.private == FIRST_PRIVATE_KEY
    assert kp.public == FIRST_PUBLIC_KEY


def test_generate_account_private_key():
    with pytest.raises(InvalidSeed):
        # Seed isn't 64 chars long
        generate_account_private_key("A"*63, 0)

    with pytest.raises(InvalidSeed):
        # Seed isn't in hex
        generate_account_private_key("G"*64, 0)

    with pytest.raises(ValueError):
        # Index is not an integer
        generate_account_private_key(SEED, None)

    assert generate_account_private_key(SEED, 0) == FIRST_PRIVATE_KEY
    assert generate_account_private_key(SEED, 1) == \
        "69def30716080acafa63a257e513b02cffce6736a566fc89afcdc81b08e54d7d"
    assert generate_account_private_key(SEED, 10) == \
        "da45500aeb14c367fb9d8bb00c9e77152c418e1e6e472858856a72d9420859fd"


def test_generate_account_key_pair():
    with pytest.raises(InvalidSeed):
        # Seed isn't 64 chars long
        generate_account_key_pair("A"*63, 0)

    with pytest.raises(InvalidSeed):
        # Seed isn't in hex
        generate_account_key_pair("G"*64, 0)

    with pytest.raises(ValueError):
        # Index isn't an integer
        generate_account_key_pair(SEED, None)

    keypair = generate_account_key_pair(SEED, 0)

    assert keypair.private == FIRST_PRIVATE_KEY
    assert keypair.public == FIRST_PUBLIC_KEY


def test_get_account_id():
    """
    Test nanolib.accounts.get_account_id
    """
    # From PUBLIC KEY
    with pytest.raises(InvalidPublicKey):
        # Public key isn't 64 chars long
        get_account_id(public_key="A"*65)

    with pytest.raises(InvalidPublicKey):
        # Public key isn't in hex
        get_account_id(public_key="G"*64)

    assert get_account_id(public_key="0"*64) == \
        "xrb_1111111111111111111111111111111111111111111111111111hifc8npp"
    assert get_account_id(public_key=FIRST_PUBLIC_KEY) == FIRST_ACCOUNT_ID_XRB

    # From PRIVATE key
    with pytest.raises(InvalidPrivateKey):
        # Private key isn't 64 chars long
        get_account_id(private_key="A"*65)

    with pytest.raises(InvalidPrivateKey):
        # Private key isn't in hex
        get_account_id(private_key="G"*64)

    assert get_account_id(private_key="0"*64) == \
        "xrb_18gmu6engqhgtjnppqam181o5nfhj4sdtgyhy36dan3jr9spt84rzwmktafc"
    assert get_account_id(private_key=FIRST_PRIVATE_KEY) == \
        FIRST_ACCOUNT_ID_XRB

    # No/multiple parameters
    with pytest.raises(TypeError):
        # More than one parameter
        get_account_id(
            private_key=FIRST_PRIVATE_KEY, public_key=FIRST_PUBLIC_KEY)

    with pytest.raises(TypeError):
        # No parameters
        get_account_id(private_key=None, public_key=None)

    # Account ID prefix
    get_account_id(public_key=FIRST_PUBLIC_KEY) == FIRST_ACCOUNT_ID_XRB
    get_account_id(
        public_key=FIRST_PUBLIC_KEY, prefix=AccountIDPrefix.NANO
    ) == FIRST_ACCOUNT_ID_NANO

    with pytest.raises(ValueError):
        # Prefix is not 'nano_' or 'xrb_'
        get_account_id(public_key=FIRST_PUBLIC_KEY, prefix="fake_")


def test_get_account_public_key():
    """
    Test nanolib.accounts.get_account_public_key
    """
    # From ACCOUNT ID
    with pytest.raises(InvalidAccount):
        # Account ID doesn't start with 'xrb_1' or 'xrb_3'
        INVALID_ACCOUNT_ID = (
            "xrb_01111111111111111111111111111111111111111111111111111111111")
        get_account_public_key(account_id=INVALID_ACCOUNT_ID)

    with pytest.raises(InvalidAccount):
        # Account ID isn't 64 chars long
        get_account_public_key(account_id="a"*63)

    with pytest.raises(InvalidAccount):
        # Character '2' not a part of Base32
        INVALID_ACCOUNT_ID = \
            "xrb_122221orwwfohx7qf13pju7144o8d4qzxizx14pua7cxsuinxzjbb6goarud"
        get_account_public_key(account_id=INVALID_ACCOUNT_ID)

    with pytest.raises(InvalidAccount):
        # Account ID doesn't have a valid checksum
        INVALID_ACCOUNT_ID = \
            "xrb_1took1orwwfohx7qf13pju7144o8d4qzxizx14pua7cxsuinxzjbb6goarue"
        get_account_public_key(account_id=INVALID_ACCOUNT_ID)

    assert get_account_public_key(account_id=FIRST_ACCOUNT_ID_XRB) == \
        FIRST_PUBLIC_KEY

    # From PRIVATE KEY
    with pytest.raises(InvalidPrivateKey):
        # Private key isn't 64 chars long
        get_account_public_key(private_key="A"*63)

    with pytest.raises(InvalidPrivateKey):
        # Private key isn't in hex
        get_account_public_key(private_key="G"*64)

    assert get_account_public_key(private_key=FIRST_PRIVATE_KEY) == \
        FIRST_PUBLIC_KEY

    # No/multiple parameters
    with pytest.raises(TypeError):
        # More than one parameter
        get_account_public_key(
            private_key=FIRST_PRIVATE_KEY, account_id=FIRST_ACCOUNT_ID_XRB)

    with pytest.raises(TypeError):
        # No parameters
        get_account_public_key(private_key=None, account_id=None)


def test_generate_account_id():
    with pytest.raises(InvalidSeed):
        # Seed isn't 64 chars long
        generate_account_id("A"*63, 0)

    with pytest.raises(InvalidSeed):
        # Seed isn't in hex
        generate_account_id("G"*64, 0)

    with pytest.raises(ValueError):
        # Index isn't an integer
        generate_account_id(SEED, None)

    assert generate_account_id(SEED, 0) == FIRST_ACCOUNT_ID_XRB


def test_is_account_id_valid():
    assert not is_account_id_valid("invalid")
    assert not is_account_id_valid(
        "xrb_4took1orwwfohx7qf13pju7144o8d4qzxizx14pua7cxsuinxzjbb6goarud")
    assert not is_account_id_valid(
        "xrb_122221orwwfohx7qf13pju7144o8d4qzxizx14pua7cxsuinxzjbb6goarud")

    assert is_account_id_valid(FIRST_ACCOUNT_ID_XRB)


def test_generate_seed():
    seed = generate_seed()

    assert len(seed) == 64
    assert is_hex(seed)
