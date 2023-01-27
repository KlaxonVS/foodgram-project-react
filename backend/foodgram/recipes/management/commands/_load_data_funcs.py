from csv import DictReader
from django.conf import settings
from json import load

from recipes.models import Ingredient, Tag

DATA_DIR = 'recipes/static/data/' if settings.DEBUG else 'static/data/'


def load_ingredients():
    """Загружает данные из файла ingredients.csv."""
    print('loading ingredients data...')
    with open(f'{DATA_DIR}ingredients.csv', encoding='utf-8') as file:
        data = DictReader(
            file, fieldnames=['name', 'measurement_unit'], delimiter=','
            )
        for row in data:
            Ingredient.objects.get_or_create(
                name=row['name'],
                measurement_unit=row['measurement_unit']
            )
    print('ingredient data loaded!')


def load_ingredients_json():
    """Загружает данные из файла ingredients.json."""
    print('loading ingredients data...')
    with open(f'{DATA_DIR}ingredients.json', encoding='utf-8') as file:
        for row in load(file):
            Ingredient.objects.get_or_create(
                name=row['name'],
                measurement_unit=row['measurement_unit']
            )
    print('user data loaded!')


def load_base_tags():
    print('loading tags data...')
    tags = [('Завтрак', "#006400", 'breakfast'),
            ('Обед', "#8B0000", 'lunch'),
            ('Ужин', "#0000FF", 'dinner')]
    for name, color, slug in tags:
        Tag.objects.get_or_create(
            name=name,
            color=color,
            slug=slug
        )
    print('tag data loaded!')
