# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 15.07.2020
"""

from dataclasses import dataclass, fields
from typing import ClassVar, List

from restfw.typing import JsonNumber, SimpleJsonValue

from .models import ValidatorModel


@dataclass()
class Validator:
    name: ClassVar[str]

    def to_model(self) -> ValidatorModel:
        args = tuple(getattr(self, f.name) for f in fields(self))
        return ValidatorModel(self.name, args)


class Required(Validator):
    name = 'required'


@dataclass()
class MinValue(Validator):
    name = 'minValue'
    min: JsonNumber


@dataclass()
class MaxValue(Validator):
    name = 'maxValue'
    max: JsonNumber


@dataclass()
class MinLength(Validator):
    name = 'minLength'
    min: int


@dataclass()
class MaxLength(Validator):
    name = 'maxLength'
    max: int


class Number(Validator):
    name = 'number'


class Email(Validator):
    name = 'email'


@dataclass()
class Regex(Validator):
    name = 'regex'
    pattern: str


@dataclass()
class Choices(Validator):
    name = 'choices'
    choices: List[SimpleJsonValue]
