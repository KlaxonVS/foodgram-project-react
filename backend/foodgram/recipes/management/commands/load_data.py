from django.core.management.base import BaseCommand

from ._load_data_funcs import load_base_tags, load_ingredients


class Command(BaseCommand):
    """Создает комманду для django,
    предназначенную для выгрузки данных из csv файлов
    в папке recipes/static/data/.
    Для запуска - python manage.py load_data.
    """

    help = ('Загружает данные из csv файлов в',
            '"recipes/static/data/" в соответствующие модели')

    def handle(self, *args, **options):
        try:
            load_ingredients()
            load_base_tags()
        except Exception as error:
            print(error)
