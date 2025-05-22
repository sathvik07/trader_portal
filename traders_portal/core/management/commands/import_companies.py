import csv
from django.core.management.base import BaseCommand
from core.models import Company

class Command(BaseCommand):
    help = "Import companies from master.csv"

    def handle(self, *args, **kwargs):
        try:
            with open("master_table.csv", newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    _, created = Company.objects.get_or_create(
                        co_code=row['co_code'].strip(),
                        company_name=row['name'].strip(),
                        symbol=row['symbol'].strip(),
                        scripcode=int(float(row['scripcode'])) if row['scripcode'] != 'NULL' else 0
                    )
                    if created:
                        count += 1
                self.stdout.write(self.style.SUCCESS(f"Imported {count} new companies."))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(" File master.csv not found. Please place it in the project root."))
