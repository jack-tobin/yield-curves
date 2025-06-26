# Create your tests here.
import datetime as dt
from decimal import Decimal
from unittest.mock import MagicMock, patch

import QuantLib as ql
from django.test import TestCase

from src.apps.yield_curves.models import Bond, BondMetric
from src.constants import DAYS_IN_YEAR


class TestBond(TestCase):
    def setUp(self) -> None:
        self.bond = Bond(
            isin="DE012346789",
            description="Bond 1",
            maturity_date=dt.date(2030, 12, 31),
            coupon=Decimal("5.0"),
            issue_volume=Decimal("1e6"),
            is_green=False,
            is_indexed=False,
        )

        self.zero_bond = Bond(
            isin="DE123467890",
            description="Bond 1",
            maturity_date=dt.date(2030, 12, 31),
            coupon=Decimal("0.0"),
            issue_volume=Decimal("1e6"),
            is_green=False,
            is_indexed=False,
        )

    def test_properties(self):
        assert self.bond.country == "DE"

    def test_quantlib_attributes(self):
        assert self.bond._ql_calendar == ql.Germany(ql.Germany.Settlement)

    @patch.object(Bond, "_build_ql_fixed_rate_bond")
    @patch.object(Bond, "_build_ql_zero_coupon_bond")
    def test_build_ql_bond(self, m_build_zero: MagicMock, m_build_fixed: MagicMock):
        _ql_bond = self.bond.build_ql_bond(dt.date(2025, 6, 25))

        m_build_zero.assert_not_called()
        m_build_fixed.assert_called_with(dt.date(2025, 6, 25))

    @patch.object(Bond, "_build_ql_fixed_rate_bond")
    @patch.object(Bond, "_build_ql_zero_coupon_bond")
    def test_build_ql_bond_zero_coupon(self, m_build_zero: MagicMock, m_build_fixed: MagicMock):
        _ql_bond = self.zero_bond.build_ql_bond(dt.date(2025, 6, 25))

        m_build_zero.assert_called_with(dt.date(2025, 6, 25))
        m_build_fixed.assert_not_called()


class TestBondMetric(TestCase):
    def setUp(self) -> None:
        self.bond = Bond(
            isin="DE012346789",
            description="Bond 1",
            maturity_date=dt.date(2030, 12, 31),
            coupon=Decimal("5.0"),
            issue_volume=Decimal("1e6"),
            is_green=False,
            is_indexed=False,
        )
        self.bond_metric = BondMetric(
            date=dt.date(2025, 6, 25),
            bond=self.bond,
            clean_price=Decimal("110.123"),
            dirty_price=Decimal("112.231"),
            _yield=Decimal("3.2342"),
        )

    def test_ttm(self):
        expected_ttm = (dt.date(2030, 12, 31) - dt.date(2025, 6, 25)).days / DAYS_IN_YEAR
        assert self.bond_metric.ttm == expected_ttm

    # def test_build_ql_bond_helper(self):
    #     expected_helper = ql.BondHelper(
    #         ql.QuoteHandle(ql.SimpleQuote(110.123)),
    #         self.bond.build_ql_bond(self.bond_metric.date),
    #     )
    #     print(self.bond_metric.build_ql_bond_helper().quote())
