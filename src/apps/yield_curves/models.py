# Create your models here.
from django.db import models

class Bond(models.Model):
    isin = models.CharField(max_length=255, primary_key=True, unique=True)
    description = models.TextField()
    maturity_date = models.DateField()
    coupon = models.DecimalField(max_digits=16, decimal_places=4)

    @property
    def country(self):
        return self.isin[:2]

    def __str__(self):
        items = {
            "country": self.country,
            "coupon": self.coupon,
            "maturity_date": self.maturity_date.isoformat()
        }
        return f"Bond({', '.join([f'{k}={v}' for k, v in items.items()])})"


class BondMetric(models.Model):
    date = models.DateField()
    isin = models.CharField(max_length=255)
    clean_price = models.DecimalField(max_digits=16, decimal_places=4)
    dirty_price = models.DecimalField(max_digits=16, decimal_places=4)
    _yield = models.DecimalField(db_column="yield",max_digits=16, decimal_places=4)

    pk = models.CompositePrimaryKey("date", "isin")
    bond = models.ForeignKey(Bond, on_delete=models.CASCADE)

    def __str__(self):
        items = {
            "bond": self.bond,
            "date": self.date.isoformat(),
        }
        return f"BondMetric({', '.join([f'{k}={v}' for k, v in items.items()])})"
