"""
nanolib.blocks
~~~~~~~~~~~~~~

Methods to work with NANO blocks and a :class:`Block` class to construct
(either manually or from JSON) and process NANO blocks
"""
from base64 import b64decode, b64encode
from binascii import hexlify, unhexlify
from functools import wraps
from hashlib import blake2b
from json import dumps, loads

from ed25519_blake2b import BadSignatureError, SigningKey, VerifyingKey

from .accounts import (get_account_id, get_account_public_key,
                       validate_account_id, validate_private_key,
                       validate_public_key)
from .exceptions import (InvalidBalance, InvalidBlock, InvalidBlockHash,
                         InvalidSignature, InvalidWork)
from .util import dec_to_hex, is_hex
from .work import (WORK_DIFFICULTY, get_work_value, parse_difficulty,
                   solve_work, validate_difficulty, validate_work)

__all__ = (
    "balance_to_hex", "parse_hex_balance", "parse_signature",
    "validate_balance", "validate_block_hash", "Block"
)


BLOCK_TYPES = ("send", "receive", "open", "change", "state")
BLOCK_PARAMS = (
    "type", "account", "previous", "destination", "representative",
    "balance", "source", "link", "link_as_account", "signature", "work"
)
BLOCK_REQUIRED_PARAMS = {
    "send": ("type", "previous", "destination", "balance"),
    "receive": ("type", "previous", "source"),
    "open": ("type", "source", "representative", "account"),
    "change": ("type", "previous", "representative"),
    "state": (
        "type", "account", "previous", "representative", "balance", "link"
    ),
}
BLOCK_OPTIONAL_PARAMS = {
    "send": ("work", "signature", "account"),
    "receive": ("work", "signature", "account"),
    "open": ("work", "signature"),
    "change": ("work", "signature", "account"),
    "state": ("work", "signature", "link_as_account")
}

# Block hash of all zeroes is used as an empty value for the 'state' field
ZERO_BLOCK_HASH = "0"*64
ZERO_ACCOUNT_ID = \
    "xrb_1111111111111111111111111111111111111111111111111111hifc8npp"


STATE_BLOCK_HEADER_BYTES = unhexlify(
    "0000000000000000000000000000000000000000000000000000000000000006")

# Constants used for epoch blocks. For details, see:
# https://github.com/nanocurrency/nano-node/pull/955
#
# 'link' value used to denote an account upgrade from V0 to V1
# The resulting bytearray starts with the string 'epoch v1 block'
EPOCH_LINK_V1 = \
    "65706F636820763120626C6F636B000000000000000000000000000000000000"
EPOCH_SIGN_PUBLIC_KEY = \
    "e89208dd038fbb269987689621d52292ae9c35941a7484756ecced92a65093ba"


MAX_BALANCE = 2**128 - 1


def block_parameter(setter):
    """Raise an error if a parameter is set to an invalid value
    """
    @wraps(setter)
    def wrapper(self, new):
        parameter = setter.__name__[4:]
        try:
            setter(self, new)
        except ValueError as e:
            raise type(e)(
                "Encountered exception while changing block parameter "
                "'{parameter}'".format(
                    parameter=parameter,
                    message=str(e))
            ) from e

    return wrapper


def invalidate_signature(setter):
    """
    Invalidate the cached value for `has_valid_signature` when the setter
    is called
    """
    @wraps(setter)
    def wrapper(self, val):
        self._has_valid_signature = None
        setter(self, val)

    return wrapper


def invalidate_work(setter):
    """
    Invalidate the cached value for `has_valid_work` when the setter
    is called
    """
    @wraps(setter)
    def wrapper(self, val):
        self._has_valid_work = None
        setter(self, val)

    return wrapper


def balance_to_hex(balance):
    """Convert a NANO balance to a 16-character hex string used in
    serialized legacy send blocks

    :param balance: Balance to convert
    :return: Balance as a 16-character hex string with necessary padding
    :rtype: str
    """
    return dec_to_hex(balance, 16)


def parse_hex_balance(balance):
    """Parse and return given hex-formatted balance as an integer.
    Hex-formatted balance is used in legacy send blocks

    :param str balance: Hex-formatted balance to convert
    :return: Converted balance
    :rtype: int
    """
    # Balance can also be given as a hexadecimal value
    if is_hex(balance) and len(balance) == 32:
        return int(balance, 16)

    raise InvalidBalance(
        "Balance for legacy send block needs to be a hexadecimal string")


def parse_signature(signature):
    """Parse a signature and return it if it's syntactically valid

    .. note:: This method only checks that the signature's format is correct.
              To verify a signature, create a :class:`Block` and use its
              :meth:`Block.verify_signature`

    :param str signature: Signature as a 128-character hex string
    :raises ValueError: Signature is invalid
    :return: Signature in uppercase
    :rtype: str
    """
    if not len(signature) == 128 or not is_hex(signature):
        raise InvalidSignature(
            "Signature has to be a 128-character hexadecimal string")

    return signature.upper()


def validate_balance(balance):
    """Validate the balance

    :param int balance: Balance
    :raises InvalidBalance: If the balance is less than 0 or higher than the
                            maximum possible balance (2^128 - 1)
    :return: Balance
    :rtype: int
    """
    if not isinstance(balance, int) or (balance < 0 or balance > MAX_BALANCE):
        raise InvalidBalance(
            "Balance has to be an integer in range 0 - (2^128 - 1)")

    return balance


def validate_block_hash(h):
    """Validate the block hash

    :param str h: Block hash as a 64-character hex string
    :raises InvalidBlockHash: If the block hash is invalid
    :return: Block hash in uppercase
    :rtype: str
    """
    if not len(h) == 64 or not is_hex(h):
        raise InvalidBlockHash(
            "Block hash has to be a 64-character hexadecimal string")

    return h.upper()


class Block(object):
    """A NANO block.

    Can be constructed manually or from a JSON string

    .. note:: For deserializing existing blocks, see \
              :meth:`Block.from_json` and :meth:`Block.from_dict`
    """
    __slots__ = (
        "_block_type", "_account", "_previous", "_destination",
        "_representative", "_balance", "_source", "_link", "_signature",
        "_work", "_difficulty", "_has_valid_signature", "_has_valid_work"
    )

    def __init__(self, block_type, verify=True, difficulty=None, **kwargs):
        """Create a block from given parameters

        .. note:: Since `type` is a Python keyword, :ivar:`block_type` is \
                  used to reference the `type` field used in NANO blocks


        :param str block_type: The type of block. Can be either
                               `send`, `receive`, `open`, `change` or `state`
        :param bool verify: If True, signature and/or the proof-of-work will
                            be verified
        :param str difficulty: Work difficulty used to check PoW's validity.
                               Default is NANO main net's default work
                               difficulty.
        :raises InvalidBlock: If the required arguments weren't provided for
                              the block type, or prohibited arguments
                              were provided
        :raises InvalidSignature: If the signature was provided but was
                                  found to be invalid
        :raises InvalidWork: If work was provided but was found to be invalid
        :raises InvalidDifficulty: If invalid work difficulty was provided
        :return: The created block
        :rtype: Block
        """
        self._has_valid_signature = None
        self._has_valid_work = None
        self.block_type = block_type

        # Set None as default value for all parameters except block_type
        for key in Block.__slots__[1:]:
            setattr(self, key, None)

        for key, value in kwargs.items():
            setattr(self, key, value)

        if not difficulty:
            difficulty = WORK_DIFFICULTY
        self.difficulty = difficulty

        self._validate(verify=verify)

    def verify_work(self, difficulty=None):
        """Verify the work in the block

        :param str difficulty: The difficulty for the proof-of-work.
                               NANO mainnet difficulty is used by default.
        :raises ValueError: If work isn't included in the block
        :raises InvalidWork: If included work doesn't meet the difficulty
        """
        if not difficulty:
            difficulty = self.difficulty

        if not self.work:
            raise ValueError("Work hasn't been added to this block")

        validate_work(
            block_hash=self.work_block_hash, work=self.work,
            difficulty=difficulty)

    def verify_signature(self):
        """Verify the signature in the block

        .. note:: :attr:`Block.account` and :attr:`Block.signature` need to \
                  be set to verify the signature

        :raises ValueError: :attr:`Block.account` or :attr:`Block.signature` \
                            isn't set
        :raises InvalidSignature: Signature was verified and found to be \
                                  invalid
        """
        if not self.account:
            raise ValueError(
                "'account' not included for signature verification. "
                "To verify the signature, the block needs to have a valid "
                "'account' value."
            )

        if not self.signature:
            raise ValueError("Signature hasn't been added to this block")

        if self.tx_type == "epoch":
            # Epoch blocks are signed by the genesis account regardless
            # of the actual account
            public_key = EPOCH_SIGN_PUBLIC_KEY
        else:
            public_key = get_account_public_key(account_id=self.account)
            validate_public_key(public_key)

        vk = VerifyingKey(unhexlify(public_key))

        try:
            vk.verify(
                sig=unhexlify(self.signature),
                msg=unhexlify(self.block_hash)
            )
        except BadSignatureError:
            raise InvalidSignature("Signature couldn't be verified")

    def sign(self, private_key):
        """Sign the block and set the value for :attr:`Block.signature`

        :raises ValueError: If the block already has a signature
        :return: True if the signature was added successfully
        :rtype: bool
        """
        if self.has_valid_signature:
            raise ValueError("The block already has a signature.")

        validate_private_key(private_key)

        sk = SigningKey(unhexlify(private_key))

        sig = sk.sign(msg=unhexlify(self.block_hash))
        self.signature = hexlify(sig).decode()

        return True

    def solve_work(self, difficulty=None, timeout=None):
        """Solve the work contained in this block and update the Block
        instance to include the work

        :raises ValueError: If the block already has valid proof-of-work
                            meeting the difficulty
        :param str difficulty: The difficulty for the proof-of-work.
                               NANO mainnet difficulty is used by default.
        :param timeout: Timeout in seconds. If provided, None will be returned
                        if the work can't be solved in the given time.
                        If None, the function will block until the work is solved.
        :type timeout: int, float or None
        :return: True if the work was solved in the given time, False otherwise
        :rtype: bool
        """
        if not difficulty:
            difficulty = self.difficulty
        else:
            self.difficulty = validate_difficulty(difficulty)

        if self.work:
            try:
                self.verify_work(difficulty=difficulty)
                raise ValueError("Block already has a valid proof-of-work")
            except InvalidWork:
                pass

        result = solve_work(
            block_hash=self.work_block_hash, difficulty=difficulty,
            timeout=timeout)

        if result:
            self.work = result
            return True

        return False

    def _validate(self, verify=True):
        """
        Make sure the block has correct parameters corresponding to its type

        .. note:: This is called automatically when creating the Block instance.
                  You don't need to call this manually.

        :param bool verify: If True, signature and/or proof-of-work will
                            be verified if included in the block
        :raises InvalidBlock: If the block has missing or prohibited parameters
        :raises InvalidSignature: If the signature was provided and was found
                                  to be invalid
        :raises InvalidWork: If work was provided and was found to be below
                             the required difficulty
        """
        block_params = set(self.to_dict().keys())
        required_params = set(BLOCK_REQUIRED_PARAMS[self.block_type])
        optional_params = set(BLOCK_OPTIONAL_PARAMS[self.block_type])

        # Check for missing params
        if len(required_params - block_params) != 0:
            missing_params = required_params - block_params
            raise InvalidBlock(
                "Block with type '{block_type}' is missing required "
                "parameters: {missing}".format(
                    block_type=self.block_type,
                    missing=", ".join(missing_params))
            )

        # Check for invalid params, excluding work and signature which are
        # optional
        if len(block_params - required_params - optional_params) != 0:
            prohibited_params = (
                block_params - required_params - optional_params)
            raise InvalidBlock(
                "Block with type '{block_type}' has prohibited parameters: "
                "{prohibited}".format(
                    block_type=self.block_type,
                    prohibited=", ".join(prohibited_params))
            )

        if verify:
            # If signature and account is included, verify the signature
            if self.signature and self.account:
                self.verify_signature()

            # If work is included, verify it
            if self.work:
                self.verify_work()

    def to_dict(self):
        """Return a :type:`dict` consisting of items used in the block
        that can be broadcast to the NANO network

        .. note:: The :ivar:`Block.block_type` has the key name `type`
                  in the created :type:`dict`

        :return: A dictionary of block items
        :rtype: dict
        """
        block_items = {}

        for param in BLOCK_PARAMS:
            if param == "type":
                param = "block_type"

            val = getattr(self, param)

            if val is not None:
                block_items[param] = val

        if block_items["block_type"]:
            block_items["type"] = block_items["block_type"]
            del block_items["block_type"]

        if "balance" in block_items.keys():
            if self.block_type == "state":
                block_items["balance"] = str(block_items["balance"])
            else:
                block_items["balance"] = balance_to_hex(
                    block_items["balance"])

        return block_items

    def json(self):
        """Return a JSON-formatted string of the block that can be
        broadcast to the NANO network

        :return: A JSON-formatted string
        :rtype: str
        """
        block_items = self.to_dict()

        return dumps(block_items)

    @classmethod
    def from_json(cls, json, verify=True, difficulty=None):
        """Create a :class:`Block` instance from a JSON-formatted string

        :param str json: A JSON-formatted block to deserialize
        :param bool verify: If True, signature and/or the proof-of-work will
                            be verified
        :param str difficulty: Work difficulty used to check PoW's validity.
                              Default is NANO main net's default work
                              difficulty.
        :return: Block
        :rtype: Block
        """
        block_items = loads(json)

        return cls.from_dict(block_items, verify=verify, difficulty=difficulty)

    @classmethod
    def from_dict(cls, d, verify=True, difficulty=None):
        """Create a :class:`Block` instance from a dictionary

        :param dict d: The block fields to deserialize
        :param bool verify: If True, signature and/or the proof-of-work will
                            be verified
        :param str difficulty: Work difficulty used to check PoW's validity.
                              Default is NANO main net's default work
                              difficulty.
        :return: Block
        :rtype: Block
        """
        d = d.copy()

        d["block_type"] = d["type"]
        del d["type"]

        if "balance" in d.keys():
            # Blocks that predate state blocks use hexadecimal balances
            if d["block_type"] == "send":
                d["balance"] = parse_hex_balance(d["balance"])
            else:
                d["balance"] = int(d["balance"])

        return cls(**d, verify=verify, difficulty=difficulty)

    @property
    def tx_type(self):
        """Return the transaction type of this block

        For blocks besides 'state', this is the same as 'block_type'. For
        'state', the type is derived from the value of 'link' field

        :return: For legacy blocks, the transaction type can be \
                 `open`, `change`, `receive` or `send`. \
                 For state blocks, the transaction type can be \
                 `change`, `open`, `send/receive` or `epoch`
        """
        if self.block_type != "state":
            return self.block_type
        elif self.link == ZERO_BLOCK_HASH:
            return "change"
        elif self.link == EPOCH_LINK_V1:
            return "epoch"
        elif self.previous == ZERO_BLOCK_HASH:
            return "open"

        return "send/receive"

    @property
    def has_valid_signature(self):
        """Check if the block has a valid signature

        :return: True if the block has a valid signature, \
                 False if either :attr:`Block.signature` or \
                 :attr:`Block.account` is missing, or if the signature \
                 was found to be invalid
        :rtype: bool
        """
        if self._has_valid_signature is not None:
            return self._has_valid_signature

        if not self.signature or not self.account:
            self._has_valid_signature = False
            return False

        try:
            self.verify_signature()
            self._has_valid_signature = True
        except InvalidSignature:
            self._has_valid_signature = False

        return self._has_valid_signature

    @property
    def has_valid_work(self):
        """Check if the block has valid work.

        .. note::

           This method assumes that NANO mainnet difficulty is used. In any
           other case use :meth:`nanolib.blocks.Block.verify_work`
           instead.

        :return: True if the block has valid work that meets the difficulty, \
                 False if :attr:`Block.work` is missing or the work
                 was found to be below the required difficulty
        :rtype: bool
        """
        if self._has_valid_work is not None:
            return self._has_valid_work

        if not self.work:
            self._has_valid_work = False
            return False

        try:
            self.verify_work()
            self._has_valid_work = True
        except InvalidWork:
            self._has_valid_work = False

        return self._has_valid_work

    @property
    def complete(self):
        """Check if the block has a valid signature and valid work

        :return: True if both the signature and work are included and both \
                 were verified to be correct, False otherwise
        :rtype: bool
        """
        return self.has_valid_signature and self.has_valid_work

    @property
    def work_block_hash(self):
        """BLAKE2b hash that requires a valid PoW

        For open blocks this is the public key derived from
        :attr:`nanolib.blocks.Block.account`. For other types of blocks,
        :attr:`nanolib.blocks.Block.previous` is used as the hash.

        :return: BLAKE2b hash used to generate a PoW
        :rtype: str

        """
        # 'open' blocks use the account ID ('account') itself as part of the
        # hash
        # Other blocks use 'previous' to make sure PoW can be completed
        # in advance (user can immediately send the transaction since PoW is
        # already ready)
        return (
            get_account_public_key(account_id=self.account)
            if self.tx_type == "open"
            else self.previous
        )

    @property
    def work_value(self):
        """The work value attached to this block. The value must be equal to
        or higher than :attr:`nanolib.blocks.Block.difficulty`
        in order to be valid.

        :return: 64-bit integer or None if this block doesn't include work
        :rtype: int or None
        """
        if self.work:
            return get_work_value(
                block_hash=self.work_block_hash, work=self.work)

        return None

    @property
    def block_hash(self):
        """BLAKE2b hash for the block used to identify the block

        :raises InvalidBlock: If the block hash can't be calculated for the \
                              block
        :return: Block hash as a 64-character hex string
        :rtype: str
        """
        if self.block_type == "receive":
            return blake2b(
                b"".join([
                    self._previous,
                    self._source
                ]),
                digest_size=32
            ).hexdigest().upper()
        elif self.block_type == "open":
            return blake2b(
                b"".join([
                    self._source,
                    unhexlify(
                        get_account_public_key(account_id=self.representative)
                    ),
                    unhexlify(
                        get_account_public_key(account_id=self.account)
                    )
                ]),
                digest_size=32
            ).hexdigest().upper()
        elif self.block_type == "change":
            return blake2b(
                b"".join([
                    self._previous,
                    unhexlify(
                        get_account_public_key(account_id=self.representative)
                    )
                ]),
                digest_size=32
            ).hexdigest().upper()
        elif self.block_type == "send":
            return blake2b(
                b"".join([
                    self._previous,
                    unhexlify(
                        get_account_public_key(account_id=self.destination)
                    ),
                    unhexlify(balance_to_hex(self.balance))
                ]),
                digest_size=32
            ).hexdigest().upper()
        elif self.block_type == "state":
            data = b"".join([
                STATE_BLOCK_HEADER_BYTES,
                unhexlify(
                    get_account_public_key(account_id=self.account)
                ),
                self._previous,
                unhexlify(
                    get_account_public_key(account_id=self.representative)
                ),
                unhexlify(balance_to_hex(self.balance)),
                self._link
            ])
            return blake2b(data, digest_size=32).hexdigest().upper()
        else:
            raise InvalidBlock(
                "Block hash can't be calculated for type {block_type}".format(
                    block_type=self.block_type)
            )

    @block_parameter
    @invalidate_signature
    def set_block_type(self, block_type):
        if block_type not in BLOCK_TYPES:
            raise ValueError("Block type is not valid")

        self._block_type = block_type

    @block_parameter
    @invalidate_signature
    @invalidate_work
    def set_account(self, account):
        if account is not None:
            validate_account_id(account)
        self._account = account

    @block_parameter
    @invalidate_signature
    @invalidate_work
    def set_source(self, source):
        if source is not None:
            validate_block_hash(source)
            self._source = unhexlify(source.encode("utf-8"))
        else:
            self._source = None

    def get_source(self):
        if not self._source:
            return None

        return hexlify(self._source).decode("utf-8").upper()

    @block_parameter
    @invalidate_signature
    @invalidate_work
    def set_previous(self, previous):
        if previous is not None:
            validate_public_key(previous)
        else:
            previous = ZERO_BLOCK_HASH

        self._previous = unhexlify(previous.encode("utf-8"))

    def get_previous(self):
        if not self._previous:
            return None

        return hexlify(self._previous).decode("utf-8").upper()

    @block_parameter
    @invalidate_signature
    def set_destination(self, destination):
        if destination is not None:
            validate_account_id(destination)
        self._destination = destination

    @block_parameter
    @invalidate_signature
    def set_representative(self, representative):
        if representative is not None:
            validate_account_id(representative)
        self._representative = representative

    @block_parameter
    @invalidate_signature
    def set_balance(self, balance):
        if balance is not None:
            validate_balance(balance)
        self._balance = balance

    @block_parameter
    @invalidate_signature
    def set_link(self, link):
        if link is not None:
            self._link = unhexlify(validate_block_hash(link).encode("utf-8"))
        else:
            self._link = unhexlify(ZERO_BLOCK_HASH.encode("utf-8"))

    def get_link(self):
        if not self._link:
            return None

        return hexlify(self._link).decode("utf-8").upper()

    @block_parameter
    @invalidate_signature
    def set_link_as_account(self, link_as_account):
        if link_as_account is not None:
            self._link = unhexlify(
                get_account_public_key(
                    account_id=link_as_account
                ).encode("utf-8")
            )
        else:
            self._link = unhexlify(ZERO_BLOCK_HASH.encode("utf-8"))

    def get_link_as_account(self):
        if not self._link:
            return None

        return get_account_id(public_key=self.link)

    @block_parameter
    @invalidate_signature
    def set_signature(self, signature):
        if signature is not None:
            self._signature = unhexlify(
                parse_signature(signature).encode("utf-8")
            )
        else:
            self._signature = None

    def get_signature(self):
        if not self._signature:
            return None

        return hexlify(self._signature).decode("utf-8").upper()

    @block_parameter
    @invalidate_work
    def set_work(self, work):
        if work is not None:
            self._work = unhexlify(work.encode("utf-8"))
        else:
            self._work = None

    def get_work(self):
        if not self._work:
            return None

        return hexlify(self._work).decode("utf-8")

    @invalidate_work
    def set_difficulty(self, difficulty):
        if difficulty is None:
            raise ValueError("'difficulty' property is required")

        self._difficulty = parse_difficulty(difficulty)

    block_type = property(lambda x: x._block_type, set_block_type)
    account = property(lambda x: x._account, set_account)
    source = property(get_source, set_source)
    previous = property(get_previous, set_previous)
    destination = property(lambda x: x._destination, set_destination)
    representative = property(lambda x: x._representative, set_representative)
    balance = property(lambda x: x._balance, set_balance)
    link = property(get_link, set_link)
    link_as_account = property(get_link_as_account, set_link_as_account)
    signature = property(get_signature, set_signature)
    work = property(get_work, set_work)
    difficulty = property(
        lambda x: dec_to_hex(x._difficulty, 8).lower(), set_difficulty
    )
