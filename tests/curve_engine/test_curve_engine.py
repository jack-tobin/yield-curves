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
                clean_price=101.0,
                dirty_price=102.0,
                _yield=5.12312,
                bond=Bond(
                    isin="DE0123456789",
                    description="Test Bond 1",
                    coupon=1,
                    maturity_date=dt.date(2026, 12, 31),
                ),
            ),
            BondMetric(
                date=dt.date(2023, 1, 1),
                clean_price=102.0,
                dirty_price=103.0,
                _yield=4.234234,
                bond=Bond(
                    isin="DE1234567890",
                    description="Test Bond 2",
                    coupon=2,
                    maturity_date=dt.date(2027, 12, 31),
                ),
            ),
        ]
        self.calibrator = YieldCurveCalibrator(bonds)
        self.calibrator.calibrate()

    def test_zero_rates(self):
        bond1 = self.calibrator.bond_metrics[0]
        date = dt.date(2023, 1, 1)

        ql_bond1 = bond1.bond.build_ql_bond(date)

        ql_bond1.setPricingEngine(self.calibrator.engine)

        assert abs(ql_bond1.cleanPrice() - bond1.clean_price) < 1e-6
