from functools import cached_property

import QuantLib as ql
from django.contrib.auth.models import User
from django.db import models

from src.constants import DAYS_IN_YEAR


class Bond(models.Model):
    isin = models.CharField(max_length=255, primary_key=True, unique=True)
    description = models.TextField()
    maturity_date = models.DateField()
    coupon = models.DecimalField(max_digits=16, decimal_places=4)
    issue_volume = models.DecimalField(max_digits=16, decimal_places=4, null=True)
    is_green = models.BooleanField(default=False)
    is_indexed = models.BooleanField(default=False)

    @property
    def country(self):
        return self.isin[:2].upper()

    def __str__(self):
        items = {
            "country": self.country,
            "coupon": self.coupon,
            "maturity_date": self.maturity_date.isoformat(),
        }
        return f"Bond({', '.join([f'{k}={v}' for k, v in items.items()])})"


class BondMetric(models.Model):
    date = models.DateField()
    isin = models.CharField(max_length=255)
    clean_price = models.DecimalField(max_digits=16, decimal_places=4)
    dirty_price = models.DecimalField(max_digits=16, decimal_places=4)
    _yield = models.DecimalField(db_column="yield", max_digits=16, decimal_places=4)

    pk = models.CompositePrimaryKey("date", "isin")
    bond = models.ForeignKey(Bond, on_delete=models.CASCADE)

    @property
    def ttm(self):
        return (self.bond.maturity_date - self.date).days / DAYS_IN_YEAR

    def __str__(self):
        items = {
            "isin": self.isin,
            "date": self.date.isoformat(),
        }
        return f"BondMetric({', '.join([f'{k}={v}' for k, v in items.items()])})"

    @cached_property
    def __ql_day_count(self) -> ql.ActualActual:
        return ql.ActualActual(ql.ActualActual.Bond)

    @cached_property
    def __ql_calendar(self) -> ql.Calendar:
        match self.country.upper():
            case "DE":
                return ql.Germany(ql.Germany.Settlement)
            case _:
                raise ValueError(f"Unsupported country: {self.country}")

    @cached_property
    def __ql_frequency(self) -> ql.Period:
        return ql.Period(ql.Semiannual)

    @cached_property
    def __ql_bond(self) -> ql.FixedRateBond:
        # Convert dates to QuantLib format
        ql_date = ql.Date(self.date.day, self.date.month, self.date.year)
        ql_maturity_date = ql.Date(
            self.maturity_date.day,
            self.maturity_date.month,
            self.maturity_date.year,
        )

        # Assume Following business convention.
        business_convention = ql.Following

        # Create schedule
        schedule = ql.Schedule(
            ql_date,
            ql_maturity_date,
            self.__ql_frequency,
            self.__ql_calendar,
            business_convention,
            business_convention,
            ql.DateGeneration.Backward,
            False,
        )

        return ql.FixedRateBond(
            settlementDaysInteger=0,
            faceAmount=100.0,
            schedule=schedule,
            coupons=[self.coupon / 100.0],
            paymentDayCounter=self.__ql_day_count,
        )

    @cached_property
    def __ql_bond_helper(self):
        # Create helper for curve building
        quote = ql.QuoteHandle(ql.SimpleQuote(self.clean_price))
        return ql.BondHelper(quote, self.__ql_bond)


class Analysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BondScatter(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name="bond_scatters")
    country = models.CharField(max_length=2)  # e.g., "DE", "US"
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def get_bond_data(self):
        """Get bond data for this scatter configuration."""
        bond_metrics = BondMetric.objects.filter(
            date=self.date,
            isin__startswith=self.country,
            bond__is_green=False,
            bond__is_indexed=False,
        ).select_related("bond")

        return bond_metrics


class YieldCurve(models.Model):
    bond_scatter = models.OneToOneField(
        BondScatter, on_delete=models.CASCADE, related_name="yield_curve"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
