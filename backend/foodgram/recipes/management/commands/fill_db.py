from django.core.management.base import BaseCommand

from recipes.management.commands import _fill_db_main


class Command(BaseCommand):
    help = 'Создание объектов модели из файла по указанному пути.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--path',
            dest='path',
            type=str,
            help='Определяет путь к папке с импортируемыми файлами',
            default=''
        )

    def handle(self, *args, **options):
        _fill_db_main.confirmation()
        _fill_db_main.run(options['path'])
        print('Complete!')
