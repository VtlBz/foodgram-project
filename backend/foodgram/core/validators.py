from typing import List, Tuple, Union

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (BaseValidator,
                                    RegexValidator)
from django.utils import timezone
from django.utils.deconstruct import deconstructible
# from rest_framework.serializers import ValidationError

user_conf = settings.USER_CREDENTIAL_SETTINGS


@deconstructible
class TextMaxLengthValidator(BaseValidator):
    """Проверяет длинну строки на соответсвие ограничению."""
    message = 'Ошибка валидации, проверьте кооректность значения'
    code = 'max_text_length'

    def compare(self, a, b):
        return a > b

    def clean(self, x):
        return len(x)


@deconstructible
class RestrictTextValidator(BaseValidator):
    """Проверяет строку на присутствие в переданном перечне."""
    message = 'Ошибка валидации, проверьте кооректность значения'
    code = 'restrict_text'

    def __init__(self,
                 limit_value: Union[str, List[str], Tuple[str]],
                 message=None):
        super().__init__(limit_value, message)
        if isinstance(limit_value, str):
            self.limit_value = (self.limit_value,)

    def compare(self, a, b):
        return a in b

    def clean(self, x):
        return x.lower()


@deconstructible
class FGUsernameValidator:
    """Валидатор логина пользователя."""
    MESSAGE_LENGTH: str = ('Длинна поля username не может '
                           'превышать {} символов')
    MESSAGE_RESTRICT: str = ('Username "me" (me/ME/Me/mE) является '
                             'зарезервированным значением. '
                             'Используйте другой username.')
    MESSAGE_CHARS: str = ('Username может содержать только '
                          'латинские буквы, цифры и знаки @/./+/-/_')

    def __init__(self):
        self.max_length_validator = TextMaxLengthValidator(
            user_conf['USERNAME_MAX_LENGTH'],
            self.MESSAGE_LENGTH.format(user_conf['USERNAME_MAX_LENGTH'])
        )
        self.restrict_name_validator = RestrictTextValidator(
            user_conf['RESTRICT_USERNAMES'],
            self.MESSAGE_RESTRICT
        )
        self.pattern_match = RegexValidator(
            user_conf['REGEX_PATTERN'],
            self.MESSAGE_CHARS,
            code='invalid_username',
            flags=0,
        )

    def __call__(self, value):
        self.max_length_validator(value)
        self.restrict_name_validator(value)
        self.pattern_match(value)


@deconstructible
class YearValidator:
    code = 'invalid_year'

    def __init__(self):
        self.result = 'OK'
        self.message = self.result
        self.current_year = timezone.now().year

    def __call__(self, value):
        self.message = self.is_valid_year(value)
        params = {'value': value}
        if self.message != self.result:
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (
            self.limit_value == other.limit_value and
            self.message == other.message and
            self.code == other.code
        )

    def is_valid_year(self, value):
        if not isinstance(value, int) or value < 0:
            self.message = f'Указан некорректный год ({value})'
        if value > self.current_year:
            self.message = 'Год не может быть больше текущего'
        return self.message
