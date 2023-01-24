from django.core.management.base import BaseCommand

from ._load_data_funcs import load_ingredients_json


class Command(BaseCommand):
    """Создает комманду для django,
    предназначенную для выгрузки данных из json файлов
    в папке recipes/static/data/.
    Для запуска - python manage.py load_data.
    """

    help = ('Загружает данные из json файлов в',
            '"recipes/static/data/" в соответствующие модели')

    def handle(self, *args, **options):
        try:
            load_ingredients_json()
        except Exception as error:
            print(error)