from django.core.management.base import BaseCommand

from recipes.management.commands import _fill_db_main


class Command(BaseCommand):
    help = 'Creating model objects according the file folder path specified'

    def add_arguments(self, parser):
        parser.add_argument(
            '-p',
            type=str,
            help='Defines the path to folder with imported files',
            default=''
        )

    def handle(self, *args, **options):
        _fill_db_main.confirmation()
        _fill_db_main.run(options['p'])
        print('Complete!')
