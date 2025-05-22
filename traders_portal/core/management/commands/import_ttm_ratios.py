import csv
from django.core.management.base import BaseCommand
from core.models import ttm_ratios, Company

class Command(BaseCommand):
    help = "Import ttm_ratios from ttm_ratios.csv"

    def handle(self, *args, **kwargs):
        try:
            with open("ttm_ratios.csv", newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    try:
                        co_code = int(row['company_id'].strip())
                        company = Company.objects.get(co_code=co_code)

                        pe = float(row['pe']) if row['pe'] != 'NULL' else None
                        roa_ttm = float(row['roa_ttm']) if row['roa_ttm'] != 'NULL' else None

                        if pe is None or roa_ttm is None:
                            self.stderr.write(self.style.WARNING(f" Skipping {co_code} due to NULL value(s)."))
                            continue

                        ttm_ratios.objects.update_or_create(
                            company=company,
                            defaults={
                                'pe': pe,
                                'roa_ttm': roa_ttm,
                            }
                        )
                        count += 1
                    except Company.DoesNotExist:
                        self.stderr.write(self.style.WARNING(f" Company with co_code {co_code} not found. Skipping."))
                    except ValueError as e:
                        self.stderr.write(self.style.WARNING(f"️ ValueError for co_code {row.get('company_id')}: {e}"))
                self.stdout.write(self.style.SUCCESS(f"✅ Imported {count} TTM ratios."))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(" File ttm_ratios.csv not found. Please place it in the project root."))
