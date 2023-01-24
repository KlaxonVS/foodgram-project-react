from csv import DictReader
from json import load

from recipes.models import Ingredient, Tag


def load_ingredients():
    """Загружает данные из файла ingredients.csv."""
    print('loading ingredients data...')
    with open('static/data/ingredients.csv', encoding='utf-8') as file:
        data = DictReader(file, fieldnames=['name', 'measurement_unit'], delimiter=',')
        ingredients = [
            Ingredient(
                name=row['name'],
                measurement_unit=row['measurement_unit'])
            for row in data
        ]
        Ingredient.objects.bulk_create(ingredients)
    print('ingredient data loaded!')

def load_ingredients_json():
    """Загружает данные из файла ingredients.json."""
    print('loading ingredients data...')
    with open('static/data/ingredients.json', encoding='utf-8') as file:
        data = load(file)
        ingredients = [
            Ingredient(
                name=row['name'],
                measurement_unit=row['measurement_unit'])
            for row in data
        ]
        Ingredient.objects.bulk_create(ingredients)
    print('user data loaded!')
    
def load_base_tags():
    print('loading tags data...')
    tags = [('Завтрак', "#006400", 'breakfast'),
            ('Обед', "#8B0000", 'lunch'),
            ('Ужин', "#0000FF", 'dinner')]
    tag_list = [
        Tag(
            name=name,
            color=color,
            slug=slug
            ) for name, color, slug in tags
    ]
    Tag.objects.bulk_create(tag_list)
    print('tag data loaded!')