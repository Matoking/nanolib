"""
nanolib.accounts
~~~~~~~~~~~~~~~~

Methods for creating keys and IDs for NANO accounts and dealing with
wallet seeds
"""

from hashlib import blake2b

from collections import namedtuple

import binascii
import random
import re
import enum

from ed25519_blake2b import SigningKey

from .exceptions import (
    InvalidSeed, InvalidAccount, InvalidPublicKey, InvalidPrivateKey
)
from .util import (
    dec_to_hex, is_hex, nbase32_to_bytes, bytes_to_nbase32
)


_AccountKeyPair = namedtuple("AccountKeyPair", ["private", "public"])


class AccountKeyPair(_AccountKeyPair):
    """NANO key pair

    :ivar str private: Private key as a 64-character hex string
    :ivar str public: Public key as a 64-character hex string
    """
    pass


class AccountIDPrefix(enum.Enum):
    """Prefixes used for NANO account IDs
    """

    XRB = "xrb_"
    """XRB prefix. Recognized universally."""

    NANO = "nano_"
    """NANO prefix. Newer prefix, may not be supported by all endpoints."""


ACCOUNT_ID_FIRST_DIGITS = ("1", "3")


def validate_private_key(private_key):
    """Validate the given private key and raise an exception on failure

    :param str private_key: Private key as a 64-character hex string
    :raises InvalidPrivateKey: If the private key is invalid
    :return: The private key
    :rtype: str
    """
    if len(private_key) != 64 or not is_hex(private_key):
        raise InvalidPrivateKey(
            "Account private key must be a 64-character hexadecimal string")

    return private_key


def validate_public_key(public_key):
    """Validate the given public key and raise an exception on failure

    :param str public_key: Public key as a 64-character hex string
    :raises InvalidPublicKey: If the public key is invalid
    :return: The public key
    :rtype: str
    """
    if len(public_key) != 64 or not is_hex(public_key):
        raise InvalidPublicKey(
            "Account public key must be a 64-character hexadecimal string")

    return public_key


def is_account_id_valid(account_id):
    """Check if the account ID is valid

    :param str account_id: Account ID as a string
    :return: True if the account ID is valid, False otherwise
    :rtype: bool
    """
    try:
        get_account_public_key(account_id=account_id)
        return True
    except InvalidAccount:
        return False


def validate_account_id(account_id):
    """Validate a NANO account ID and raise an exception on failure

    :param str account_id: Account ID as a string
    :raises InvalidAccount: If the account ID is invalid
    :return: The account ID
    :rtype: str
    """
    get_account_public_key(account_id=account_id)
    return account_id


def validate_seed(seed):
    """Validate a NANO seed and raise an exception on failure

    :param str seed: Seed as a 64-character hex string
    :raises InvalidSeed: If the seed is invalid
    :return: The seed
    :rtype: str
    """
    if len(seed) != 64 or not is_hex(seed):
        raise InvalidSeed("Seed must be a 64-character hexadecimal string")

    return seed


def get_account_key_pair(private_key):
    """Generate a public key from a private key and return the key pair

    :param private_key: Private key as a 64-character hex string
    :raises InvalidPrivateKey: If the private key is invalid
    :return: Return the key pair
    :rtype: AccountKeyPair
    """
    validate_private_key(private_key)

    signing_key = SigningKey(binascii.unhexlify(private_key))
    private_key = signing_key.to_bytes().hex()
    public_key = signing_key.get_verifying_key().to_bytes().hex()

    return AccountKeyPair(private=private_key, public=public_key)


def generate_account_private_key(seed, index):
    """Generate account's private key from a 32-byte seed and index

    :param str seed: Seed as a 64-character hex string
    :param int index: Index of the account private key to generate
    :raises InvalidSeed: If the seed is invalid
    :raises ValueError: If the index isn't an integer
    :return: Account private key as a 64-character hex string
    :rtype: str
    """
    validate_seed(seed)

    if not isinstance(index, int):
        raise ValueError("Index must be an integer")

    account_bytes = binascii.unhexlify(dec_to_hex(index, 4))
    context = blake2b(digest_size=32)
    context.update(binascii.unhexlify(seed))
    context.update(account_bytes)

    new_key = context.hexdigest()
    return new_key


def generate_account_key_pair(seed, index):
    """Generate an account key pair from a 32-byte seed and index

    :param str seed: Seed as a 64-character hex string
    :param int index: Index of the account key pair to generate
    :raises InvalidSeed: If the seed is invalid
    :raises ValueError: If the index isn't an integer
    :return: Account public and private key pair
    :rtype: AccountKeyPair
    """
    private_key = generate_account_private_key(seed, index)
    _, public_key = get_account_key_pair(private_key)

    return AccountKeyPair(private=private_key, public=public_key)


def get_account_id(*, public_key=None, private_key=None, prefix=None):
    """Get NANO account ID by using either a public key or a private key

    .. note:: Parameters `public_key` and `private_key` are mutually exclusive \
              and have to be given as keyword arguments

    :param str public_key: Public key as a 64-character hex string
    :param str private_key: Private key as a 64-character hex string
    :param str prefix: (optional) Prefix to use for the account ID. \
                       Can be either :const:`AccountIDPrefix.NANO` or \
                       :const:`AccountIDPrefix.XRB`. \
                       Defaults to :const:`AccountIDPrefix.XRB`

    :raises ValueError: If the given prefix isn't either XRB or NANO
    :raises TypeError: If both private and public keys are given, or if \
                       none are given as named parameter
    :raises InvalidPublicKey: If the given public key is invalid
    :raises InvalidPrivateKey: If the given private key is invalid
    :return: Account ID
    :rtype: str

     Usage::

      >>> from nanolib.accounts import get_account_id, AccountIDPrefix
      >>> get_account_id(private_key="2"*64)
      'xrb_1iwamgozb5ckj9zzojbnb79485dfiw8jegedzwzuzy5b4a19cbs8b4tsdzo3'
      >>> get_account_id(public_key="2"*64)
      'xrb_1aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj4ykus34mi'
      >>> get_account_id(public_key="2"*64, prefix=AccountIDPrefix.NANO)
      'nano_1aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj4ykus34mi'
      >>> get_account_id(public_key="2"*64, prefix="nano_")
      'nano_1aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj4ykus34mi'

    """
    def _from_public_key(public_key, prefix):
        """
        Derive NANO account ID from a public key
        """
        validate_public_key(public_key)

        public_key_bytes = binascii.unhexlify(public_key)

        account = bytes_to_nbase32(public_key_bytes)
        checksum_bytes = blake2b(public_key_bytes, digest_size=5).digest()
        checksum_bytes = bytearray(checksum_bytes)
        checksum_bytes.reverse()
        checksum = bytes_to_nbase32(checksum_bytes)

        return "{prefix}{account}{checksum}".format(
            prefix=prefix, account=account, checksum=checksum)

    def _from_private_key(private_key, prefix):
        """
        Derive NANO account ID from a private key
        """
        _, public_key = get_account_key_pair(private_key=private_key)
        return _from_public_key(public_key=public_key, prefix=prefix)

    if not prefix:
        prefix = AccountIDPrefix.XRB
    try:
        prefix = AccountIDPrefix(prefix)
    except ValueError:
        raise ValueError(
            "Account ID prefix has to be one of the following: "
            "{prefixes}".format(prefixes=",".join(
                AccountIDPrefix._value2member_map_)
            )
        )

    if public_key and private_key:
        raise TypeError(
            "Only either 'public_key' or 'private_key' parameter can be given")
    elif not public_key and not private_key:
        raise TypeError(
            "Either 'public_key' or 'private_key' has to be given as a named "
            "parameter")

    if public_key:
        return _from_public_key(public_key, prefix.value)
    elif private_key:
        return _from_private_key(private_key, prefix.value)


def get_account_public_key(*, account_id=None, private_key=None):
    """Get a NANO public key using either an account ID or a private key

    .. note:: Parameters `account_id` and `private_key` are mutually exclusive \
              and have to be given as keyword arguments

    :param str account_id: Account ID
    :param str private_key: Private key as a 64-character hex string
    :raises TypeError: If both account ID and private key are given, or if \
                       none are given as keyword arguments
    :raises InvalidAccount: If the given account ID is invalid
    :raises InvalidPrivateKey: If the given private key is invalid
    :return: Public key as a 64-character hex string
    :rtype: str
    """

    def _from_account_id(account_id):
        try:
            account_prefix = account_id[0:account_id.index("_")+1]
            account_rest = account_id[account_id.index("_")+1:]
        except ValueError:
            raise InvalidAccount("Invalid NANO address")

        if account_prefix not in AccountIDPrefix._value2member_map_ or \
                account_rest[0] not in ACCOUNT_ID_FIRST_DIGITS or \
                len(account_rest) != 60:
            raise InvalidAccount("Invalid NANO address")

        valid_regex = "^[13456789abcdefghijkmnopqrstuwxyz]+$"
        if not re.match(valid_regex, account_rest):
            raise InvalidAccount("Invalid NANO address")

        public_key_bytes = nbase32_to_bytes(account_rest[0:52])
        account_checksum_bytes = nbase32_to_bytes(account_rest[52:60])

        key_checksum_bytes = bytearray(
            blake2b(public_key_bytes, digest_size=5).digest()
        )
        key_checksum_bytes.reverse()

        if key_checksum_bytes != account_checksum_bytes:
            raise InvalidAccount("Invalid checksum")

        return binascii.hexlify(public_key_bytes).decode()

    def _from_private_key(private_key):
        _, public_key = get_account_key_pair(private_key=private_key)

        return public_key

    if account_id and private_key:
        raise TypeError(
            "Only either 'account_id' or 'private_key' parameter can be given")
    elif not account_id and not private_key:
        raise TypeError(
            "Either 'account_id' or 'private_key' has to be given as a named "
            "parameter")

    if account_id:
        return _from_account_id(account_id)
    elif private_key:
        return _from_private_key(private_key)


def generate_account_id(seed, index):
    """Derive an account ID from a seed and an index

    :param str seed: Seed as a 64-character hex string
    :param int index: Index of the account ID to generate
    :return: Account ID
    :rtype: str
    """
    _, public_key = generate_account_key_pair(seed, index)
    account_id = get_account_id(public_key=public_key)

    return account_id


def generate_seed():
    """
    Generate a secure random 64-character hexadecimal seed for use in
    generating NANO accounts

    :return: Seed as a 64-character hex string
    :rtype: str
    """
    gen = random.SystemRandom()
    return "".join([gen.choice("0123456789abcdef") for _ in range(0, 64)])
