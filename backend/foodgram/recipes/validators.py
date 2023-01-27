import re

from django.core.exceptions import ValidationError


def validate_hex(hex):
    """Проверка цвета в HEX кодировке."""
    if not re.fullmatch(r'^#[0-9A-F]{6}$', hex):
        raise ValidationError(
            'color должен быть задан HEX кодировкой в верхнем регистре\n'
            'Например: #ADD8E6 - LightBlue'
        )
