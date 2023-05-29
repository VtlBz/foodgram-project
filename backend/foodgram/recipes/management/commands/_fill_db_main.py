import csv
import logging
import os

from django.apps import apps

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

EXIT_COMMANDS_LIST: tuple = ('no', 'n', 'нет', 'н', 'q', 'quit', 'exit',)
CONTINUE_COMMANDS_LIST: tuple = ('yes', 'y', 'да', 'д',)

ERROR_MESSAGE_FILENOTFOUND: str = ('Ошибка обработки запроса. '
                                   'Файла с именем {} не существует '
                                   'в указанной директории.')
ERROR_MESSAGE_CONSTRAINT: str = ('Для корректной обработки импорта '
                                 'имя файла должно соответствовать '
                                 'указанному в таблице соответствия.')


FILE_NAME = 'ingredients.csv'
APP_MODEL = 'recipes.Ingredient'


def confirmation() -> None:
    print('Данный скрипт импортирует данные '
          'из .csv файлов в базу данных проекта.')
    print(f'{FILE_NAME} --> {APP_MODEL}')
    print('Импорт будет произведён в указанном выше порядке и'
          'в соответствии со связью <имя_файла> --> <app_name>.<Model_name>')
    print('Проверьте соответствие имён файлов в каталоге '
          'на соответствие указанным выше, прежде чем продолжить.')

    while True:
        q = input('Подтвердить (yes/no)? ') or ''
        if q.lower() in CONTINUE_COMMANDS_LIST:
            break
        if q.lower() in EXIT_COMMANDS_LIST:
            raise SystemExit('Операция отменена пользователем')
        print('Ошибка! Команда не распознана!')
        print('Допустимые значения:')
        print(f'Подтвердить и продолжить - {CONTINUE_COMMANDS_LIST}')
        print(f'Отменить и выйти - {EXIT_COMMANDS_LIST}')


def get_file_path(folder_path, file_name) -> str:
    err_msg = ERROR_MESSAGE_FILENOTFOUND.format
    for root, dirs, files in os.walk(folder_path):
        if file_name in files:
            return str(os.path.join(root, file_name))
        logger.error(err_msg(file_name))
        raise SystemExit(ERROR_MESSAGE_CONSTRAINT)


def process_table(reader, _model, file_name) -> None:
    header = ('name', 'measurement_unit',)
    row_count = row_success = 0
    for row in reader:
        _object_dict = {key: value for key, value
                        in zip(header, row)}
        _, is_create = _model.objects.get_or_create(**_object_dict)
        row_count += 1
        if is_create:
            row_success += 1
    logger.info(f'Конец обработки файла {file_name}, '
                f'обработано строк - {row_count}, '
                f'успешно создано - {row_success}.')


def run(folder_path) -> None:
    app_name, model_name = APP_MODEL.split('.')
    file_path = get_file_path(folder_path, FILE_NAME)
    logger.info(f'Начало обработки модели {app_name}.{model_name}')
    _model = apps.get_model(app_label=app_name, model_name=model_name)
    logger.info(f'Начало обработки файла {FILE_NAME}')
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        process_table(reader, _model, FILE_NAME)
