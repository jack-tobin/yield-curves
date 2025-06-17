"""Bond Yield Curve Calibration Engine using QuantLib

This module provides a high-level interface for calibrating yield curves
from bond market data using QuantLib's numerical methods.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import overload

import QuantLib as ql

from src.apps.yield_curves.models import BondMetric


class CurveMethod(Enum):
    LINEAR_ZERO = ql.PiecewiseLinearZero
    CUBIC_ZERO = ql.PiecewiseCubicZero
    LOG_LINEAR_DISCOUNT = ql.PiecewiseLogLinearDiscount
    NATURAL_LOG_CUBIC_DISCOUNT = ql.PiecewiseNaturalLogCubicDiscount


@dataclass(frozen=True)
class FixedCouponBond:
    maturity_date: dt.date
    coupon: float
    price: float
    _yield: float
    valuation_date: dt.date
    face_value: float = 100.0

    @classmethod
    def from_bond_metric(cls, bond_metric: BondMetric) -> FixedCouponBond:
        return cls(
            maturity_date=bond_metric.maturity_date,
            coupon=bond_metric.coupon,
            price=bond_metric.price,
            _yield=bond_metric._yield,
            valuation_date=bond_metric.valuation_date,
        )


class YieldCurveCalibrator:
    def __init__(
        self,
        bonds: list[BondMetric],
        valuation_date: dt.date | None = None,
    ):
        self.bonds: list[BondMetric] = bonds
        self.valuation_date = valuation_date or date.today()

        self.curve: ql.YieldTermStructure | None = None

        ql_date = ql.Date(
            self.valuation_date.day, self.valuation_date.month, self.valuation_date.year
        )
        ql.Settings.instance().evaluationDate = ql_date

    def calibrate(
        self,
        method: CurveMethod = CurveMethod.CUBIC_ZERO,
        accuracy: float = 1e-8,
    ) -> YieldCurveCalibrator:
        if not self.bonds:
            raise ValueError("No bonds added for calibration")
        helpers = [bond.__ql_bond_helper for bond in self.bonds]
        ql_valuation_date = ql.Date(
            self.valuation_date.day, self.valuation_date.month, self.valuation_date.year
        )
        day_count = next(bond.__ql_day_count for bond in self.bonds)
        self.curve = method.value(ql_valuation_date, helpers, day_count, accuracy)

    @overload
    def zero_rate(self, ttm: float) -> float:
        if not self.curve:
            raise ValueError("Curve not calibrated yet")
        return self.curve.zeroRate(ttm, ql.Compounded).rate()

    def forward_rate(
        self,
        forward_start: float,
        ttm: float,
    ) -> float:
        if not self.curve:
            raise ValueError("Curve not calibrated yet")
        return self.curve.forwardRate(forward_start, ttm, ql.Compounded).rate()

    def discount_factor(self, ttm: float) -> float:
        if not self.curve:
            raise ValueError("Curve not calibrated yet")
        return self.curve.discount(ttm)
