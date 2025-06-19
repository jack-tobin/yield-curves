import datetime as dt

from django.test import TestCase

from src.apps.yield_curves.models import (
    Bond,
    BondMetric,
)
from src.curve_engine.curve_engine import (
    YieldCurveCalibrator,
)


class TestCalibrator(TestCase):
    def setUp(self):
        bonds = [
            BondMetric(
                date=dt.date(2023, 1, 1),
                clean_price=87.32539923318181,
                dirty_price=87.32539923318181,
                _yield=4.5,
                bond=Bond(
                    isin="DE0123456789",
                    description="Test Bond 1",
                    coupon=1,
                    maturity_date=dt.date(2026, 12, 31),
                ),
            ),
            BondMetric(
                date=dt.date(2023, 1, 1),
                clean_price=84.887064781726,
                dirty_price=84.887064781726,
                _yield=5.5,
                bond=Bond(
                    isin="DE1234567890",
                    description="Test Bond 2",
                    coupon=2,
                    maturity_date=dt.date(2027, 12, 31),
                ),
            ),
            BondMetric(
                date=dt.date(2023, 1, 1),
                clean_price=68.13904096546891,
                dirty_price=68.13904096546891,
                _yield=6.394454706633495,
                bond=Bond(
                    isin="DE2345678901",
                    description="Test Bond 3",
                    coupon=0.0,  # Zero coupon.
                    maturity_date=dt.date(2028, 12, 31),
                ),
            ),
        ]
        self.calibrator = YieldCurveCalibrator(bonds, valuation_date=dt.date(2023, 1, 1))
        self.calibrator.calibrate()

    def test_clean_price(self):
        bond1 = self.calibrator.bond_metrics[0]
        date = dt.date(2023, 1, 1)

        ql_bond1 = bond1.bond.build_ql_bond(date)
        ql_bond1.setPricingEngine(self.calibrator.engine)

        assert abs(ql_bond1.cleanPrice() - bond1.clean_price) < 1e-6

    def test_zero_rate(self):
        bond3 = next(
            bond_metric
            for bond_metric in self.calibrator.bond_metrics
            if bond_metric.bond.coupon == 0.0
        )
        zero_rate_calibrated = self.calibrator.zero_rate(bond3.ttm) * 100.0
        assert abs(zero_rate_calibrated - bond3._yield) < 1e-6, (
            f"expected {bond3._yield}, got {zero_rate_calibrated}"
        )
