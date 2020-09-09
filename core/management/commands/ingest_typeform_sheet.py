import argparse

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Ingest Typeform Sheets'

    def add_arguments(self, parser):
        parser.add_argument(
            'sheet',
            type=argparse.FileType('r'),
            help=''
        )

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)
