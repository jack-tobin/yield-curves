"""Bond Yield Curve Calibration Engine using QuantLib

This module provides a high-level interface for calibrating yield curves
from bond market data using QuantLib's numerical methods.
"""

from __future__ import annotations

import datetime as dt
from datetime import date

import QuantLib as ql

from src.apps.yield_curves.models import BondMetric


class YieldCurveCalibrator:
    """Bond Yield Curve Calibration Engine using QuantLib

    This class provides a high-level interface for calibrating yield curves
    from bond market data using QuantLib's numerical methods.

    Current implementation is to fit a Nelson-Siegel curve.
    """

    def __init__(
        self,
        bond_metrics: list[BondMetric],
        valuation_date: dt.date | None = None,
    ):
        self.bond_metrics: list[BondMetric] = bond_metrics
        self.valuation_date = valuation_date or date.today()

        self.curve: ql.YieldTermStructure | None = None

        ql_date = ql.Date(
            self.valuation_date.day, self.valuation_date.month, self.valuation_date.year
        )
        ql.Settings.instance().evaluationDate = ql_date

    def calibrate(self) -> YieldCurveCalibrator:
        helpers = [
            bond_metric.build_ql_bond_helper()
            for bond_metric in self.bond_metrics
            if bond_metric.ttm > 0
        ]
        if not self.bond_metrics:
            raise ValueError("No bonds added for calibration")
        ql_valuation_date = ql.Date(
            self.valuation_date.day, self.valuation_date.month, self.valuation_date.year
        )
        day_count = next(bond_metric.bond._ql_day_count for bond_metric in self.bond_metrics)
        self.curve = ql.FittedBondDiscountCurve(
            ql_valuation_date,
            helpers,
            day_count,
            ql.SvenssonFitting(),
        )

    @property
    def engine(self):
        return ql.DiscountingBondEngine(ql.YieldTermStructureHandle(self.curve))

    def zero_rate(self, ttm: float) -> float:
        if not self.curve:
            raise ValueError("Curve not calibrated yet")
        return self.curve.zeroRate(ttm, ql.Continuous).rate()

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
