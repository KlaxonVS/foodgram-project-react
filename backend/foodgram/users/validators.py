import re

from django.core.exceptions import ValidationError


def validate_username(name):
    """Делает невозможным использовать <<me>> как имя"""
    if name.lower() == 'me':
        raise ValidationError('Нельзя использовать "me" как username')
    if not re.fullmatch(r'^[\w.@+-]+\Z', name):
        letters = []
        for letter in name:
            re.match(r'^[\w.@+-]+\Z', letter)
            letters.append(letter)
        raise ValidationError('username может состоять только'
                              ' из букв, цифр и @/./+/-/_\n'
                              f'Вы использовали: {letters}')
