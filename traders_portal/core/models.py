from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Company(models.Model):
    co_code = models.IntegerField(db_index=True)
    company_name = models.CharField(max_length=255, db_index=True)
    symbol = models.CharField(max_length=20, db_index=True)
    scripcode = models.IntegerField(db_index=True)

    def __str__(self):
        return f"{self.company_name} ({self.symbol})"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist', db_index=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, db_index=True)

    class Meta:
        unique_together = ('user', 'company')

    def __str__(self):
        return f"{self.user.username} - {self.company.symbol}"


class ttm_ratios(models.Model):
    pe = models.FloatField(db_index=True)
    roa_ttm = models.FloatField(db_index=True)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, db_index=True, related_name='ttm_ratios')

    def __str__(self):
        return f"{self.company.company_name} - {self.pe} - {self.roa_ttm}"