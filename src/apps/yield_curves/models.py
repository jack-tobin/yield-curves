from django.contrib.auth.models import User
from django.db import models


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
        return self.isin[:2]

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

    def __str__(self):
        items = {
            "isin": self.isin,
            "date": self.date.isoformat(),
        }
        return f"BondMetric({', '.join([f'{k}={v}' for k, v in items.items()])})"


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
