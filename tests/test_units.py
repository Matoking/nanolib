from decimal import Decimal

import pytest
from nanocurrency.units import convert, NanoDenomination


def test_floats_not_allowed():
    with pytest.raises(TypeError):
        convert(1.5, source=NanoDenomination.NANO, target=NanoDenomination.RAW)


@pytest.mark.parametrize("raw,knano", [
    (123456789, Decimal("0.000000000000000000123456789")),
    (1, Decimal("0.000000000000000000000000001")),
    (Decimal("123456789"), Decimal("0.000000000000000000123456789")),
    (Decimal("1"), Decimal("0.000000000000000000000000001")),
])
def test_knano_conversions(raw, knano):
    assert convert(
        raw, source=NanoDenomination.RAW, target=NanoDenomination.KILONANO
    ) == knano
    assert convert(
        knano, source=NanoDenomination.KILONANO, target=NanoDenomination.RAW
    ) == raw


@pytest.mark.parametrize("raw,mnano", [
    (123456789, Decimal("0.000000000000000000000123456789")),
    (1, Decimal("0.000000000000000000000000000001")),
    (Decimal("123456789"), Decimal("0.000000000000000000000123456789")),
    (Decimal("1"), Decimal("0.000000000000000000000000000001")),
])
def test_mnano_conversions(raw, mnano):
    assert convert(
        raw, source=NanoDenomination.RAW, target=NanoDenomination.MEGANANO
    ) == mnano
    assert convert(
        mnano, source=NanoDenomination.MEGANANO, target=NanoDenomination.RAW
    ) == raw


@pytest.mark.parametrize("raw,nano", [
    (123456789, Decimal("0.000000000000000123456789")),
    (1, Decimal("0.000000000000000000000001")),
    (Decimal("123456789"), Decimal("0.000000000000000123456789")),
    (Decimal("1"), Decimal("0.000000000000000000000001")),
])
def test_nano_conversions(raw, nano):
    assert convert(
        raw, source=NanoDenomination.RAW, target=NanoDenomination.NANO
    ) == nano
    assert convert(
        nano, source=NanoDenomination.NANO, target=NanoDenomination.RAW
    ) == raw


def test_max_nano_value():
    with pytest.raises(ValueError):
        # Value is larger than (2**128)-1 raw
        convert(
            Decimal("340282366.920938463463374607431768211456"),
            source=NanoDenomination.MEGANANO,
            target=NanoDenomination.RAW)

    with pytest.raises(ValueError):
        # Value is larger than (2**128)-1 raw
        convert(
            Decimal("340282366920938463463374607431768211456"),
            source=NanoDenomination.RAW,
            target=NanoDenomination.MEGANANO)

    convert(
        Decimal("340282366.920938463463374607431768211455"),
        source=NanoDenomination.MEGANANO,
        target=NanoDenomination.RAW
    ) == Decimal("340282366920938463463374607431768211455")

    convert(
        Decimal("340282366920938463463374607431768211455"),
        source=NanoDenomination.RAW,
        target=NanoDenomination.MEGANANO
    ) == Decimal("340282366.920938463463374607431768211455")
