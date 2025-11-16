import asyncio
from django.core.management.base import BaseCommand
from tg_parser.main import run

class Command(BaseCommand):
    help = 'Запуск TG парсера'

    def handle(self, *args, **options):
        self.stdout.write('Tg_parser started')
        asyncio.run(run())

