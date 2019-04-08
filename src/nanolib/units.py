"""
nanolib.units
~~~~~~~~~~~~~

Methods for converting between different NANO denominations.

The smallest possible denomination is known as `raw`. The other
common denominations are:

* 1 nano = :math:`10^{24}` raw
* 1 knano = :math:`10^{27}` raw
* 1 Mnano/NANO = :math:`10^{30}` raw


Or in other words:

* 1 NANO = 1 000 000 nano
* 1 000 knano = 1 NANO
* 1 Mnano = 1 000 knano
* 1 Mnano = 1 000 000 nano
* 1 Mnano = 1 NANO

.. warning::
    Note that `nano` and `NANO` are **not** interchangeable!
    If you are using the denominations in a context where they may cause
    confusion, consider using `nano` and `Mnano` instead.

.. note::
    Denominations `XRB`/`Mrai`, `Krai` and `xrb`/`rai` were used before
    RaiBlocks' rebranding as NANO. The corresponding old names for
    these denominations are:

    * Mnano/NANO = Mrai/XRB
    * knano = kRAI
    * Mnano = Mrai
    * nano = xrb/rai

.. note::
    Consider storing all NANO values as integers using the `raw` denomination
    and only converting the value to another denomination
    when presenting a human-readable amount.
    `nanolib` uses Python's Decimal library and increases
    precision on startup to account for precision loss.
    This precision can be changed during runtime by another library.

"""
import functools
import enum
from decimal import Decimal, Inexact, getcontext

# Increase precision for Decimals in order to make it suitable for
# handling NANO denominations
getcontext().prec = 39
getcontext().traps[Inexact] = 1


__all__ = (
    "convert", "NanoDenomination", "NANO_RAW_CAP",
)


NANO_RAW_CAP = (2**128)-1


class NanoDenomination(enum.Enum):
    """Denominations used in NANO"""

    RAW = "raw"
    """Smallest division used in NANO"""

    MICRONANO = "unano"
    """1 unano = :math:`10^{18}` `raw`"""

    MILLINANO = "millinano"
    """1 mnano = :math:`10^{21}` `raw`"""

    NANO = "nano"
    """1 nano = :math:`10^{24}` `raw`"""

    KILONANO = "knano"
    """1 knano = :math:`10^{27}` `raw`"""

    MEGANANO = "Mnano"
    """1 Mnano = :math:`10^{30}` `raw`"""

    GIGANANO = "Gnano"
    """1 Gnano = :math:`10^{33}` `raw`"""


NANO_RAW_AMOUNTS = {
    NanoDenomination.RAW.value: Decimal("1"),
    NanoDenomination.MICRONANO.value: Decimal("1000000000000000000"),
    NanoDenomination.MILLINANO.value: Decimal("1000000000000000000000"),
    NanoDenomination.NANO.value: Decimal("1000000000000000000000000"),
    NanoDenomination.KILONANO.value: Decimal("1000000000000000000000000000"),
    NanoDenomination.MEGANANO.value:
        Decimal("1000000000000000000000000000000"),
    NanoDenomination.GIGANANO.value:
        Decimal("1000000000000000000000000000000000"),
}


def _forbid_float(func):
    """Decorator that only allows an integer or a Decimal as the first argument
    """
    @functools.wraps(func)
    def _decorator(*args, **kwargs):
        if not isinstance(args[0], int) and not isinstance(args[0], Decimal):
            raise TypeError(
                "Value has to be an integer or a Decimal. "
                "Floating numbers cause precision loss and are unsuitable "
                "for handling monetary values."
            )
        else:
            return func(*args, **kwargs)

    return _decorator


@_forbid_float
def convert(amount, source, target):
    """Convert an amount from one denomination to another

    :param amount: Amount to convert
    :type amount: decimal.Decimal or int
    :param NanoDenomination source: The denomination to convert from
    :param NanoDenomination target: The denomination to convert to
    :raises ValueError: If the amount is higher than the NANO coin cap \
                        (:math:`2^{128} - 1` `raw`)
    :raises TypeError": If `amount`  is not an `int` or a
                        :class:`decimal.Decimal`

    :return: Converted amount
    :rtype: decimal.Decimal
    """
    source = NanoDenomination(source)
    target = NanoDenomination(target)

    raw_source = NANO_RAW_AMOUNTS[source.value]
    raw_target = NANO_RAW_AMOUNTS[target.value]

    # Convert first into raw, then into the target denomination
    raw_amount = amount * raw_source

    if raw_amount > NANO_RAW_CAP:
        raise ValueError("Amount is higher than the NANO coin supply")

    raw_amount /= raw_target

    return raw_amount
