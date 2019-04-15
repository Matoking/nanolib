from ed25519_blake2b import BadSignatureError


__all__ = (
    "InvalidBlock", "InvalidWork", "InvalidThreshold", "InvalidSignature",
    "InvalidBlockHash", "InvalidBalance", "InvalidSeed", "InvalidAccount",
    "InvalidPrivateKey", "InvalidPublicKey"
)


class InvalidBlock(ValueError):
    """The block is invalid."""


class InvalidWork(ValueError):
    """The given work is invalid."""


class InvalidThreshold(ValueError):
    """The given work threshold is invalid."""


class InvalidSignature(BadSignatureError):
    """The given signature is invalid."""


class InvalidBlockHash(ValueError):
    """The given block hash is invalid."""


class InvalidBalance(ValueError):
    """The given balance is invalid."""


class InvalidSeed(ValueError):
    """The seed is invalid."""


class InvalidAccount(ValueError):
    """The NANO account ID is invalid."""


class InvalidPrivateKey(ValueError):
    """The NANO private key is invalid."""


class InvalidPublicKey(ValueError):
    """The NANO public key is invalid."""
