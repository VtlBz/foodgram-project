from typing import List, Tuple, Union

from django.conf import settings
from django.core.validators import (
    BaseValidator, MaxValueValidator, RegexValidator,
)
from django.utils.deconstruct import deconstructible

user_conf = settings.USER_CREDENTIAL_SETTINGS


class TextMaxLengthValidator(MaxValueValidator):
    """Проверяет длинну строки на соответсвие ограничению."""
    message = 'Ошибка валидации, проверьте кооректность значения'
    code = 'max_text_length'

    def clean(self, x):
        return len(x)


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
class UsernameValidator:
    """Валидатор логина пользователя."""
    MESSAGE_LENGTH: str = ('Длинна поля не может '
                           'превышать {} символов')
    MESSAGE_RESTRICT: str = ('Имя пользователя "me" (me/ME/Me/mE) '
                             'является зарезервированным значением. '
                             'Используйте друге имя пользователя.')
    MESSAGE_CHARS: str = ('Имя пользователя может содержать только '
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
