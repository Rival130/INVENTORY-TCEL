# modules/reports/management/commands/take_stock_snapshot.py
# (kria pasta: modules/reports/management/__init__.py no modules/reports/management/commands/__init__.py)
from datetime import date

from django.core.management.base import BaseCommand, CommandError

from modules.reports.services import init_price_history, take_snapshot


class Command(BaseCommand):
    help = "Foti snapshot stock (loron-loron). Uza --init-prices dala ida de'it atu kria istória folin inisiál."

    def add_arguments(self, parser):
        parser.add_argument("--date", help="Data snapshot (YYYY-MM-DD). Default: ohin.")
        parser.add_argument("--init-prices", action="store_true", help="Kria istória folin inisiál ba produtu hotu.")

    def handle(self, *args, **options):
        if options["init_prices"]:
            n = init_price_history()
            self.stdout.write(self.style.SUCCESS(f"Istória folin inisiál: {n} produtu."))

        day = None
        if options.get("date"):
            try:
                day = date.fromisoformat(options["date"])
            except ValueError:
                raise CommandError("Formatu data tenke YYYY-MM-DD.")

        snapshot_date, count = take_snapshot(day)
        self.stdout.write(self.style.SUCCESS(f"Snapshot {snapshot_date}: {count} liña stock."))


# Agenda loron-loron (ezemplu Linux cron, 23:55):
#   55 23 * * * cd /path/projetu && /path/venv/bin/python manage.py take_stock_snapshot
# Windows: uza Task Scheduler ho komandu "python manage.py take_stock_snapshot".