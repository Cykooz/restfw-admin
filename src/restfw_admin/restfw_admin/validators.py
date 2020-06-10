# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 27.04.2020
"""
from inspect import isfunction
from typing import Any, Callable, Generator, List, Optional, Type

import colander
import venusian
from pyramid.config import Configurator
from pyramid.registry import Registry
from restfw import schemas
from zope.interface import implementer

from . import interfaces
from .models import ValidatorModel
from .typing import ColanderNode, ColanderValidator


__all__ = [
    'ValidatorConverter',
    'add_validator_converter',
    'validator_converter',
    'get_validators',
    'get_validators_by_name',
    'get_validator_models',
]


ValidatorConverter = Callable[
    [Registry, ColanderValidator],
    Generator[ValidatorModel, Any, None]
]


@implementer(interfaces.IColanderValidator)
class _FunctionBasedValidator:

    def __init__(self, validator: ColanderValidator):
        self.__call__ = validator


def get_validators(registry: Registry, node: ColanderNode) -> List[ValidatorModel]:
    validators = []
    if node.missing is colander.required:
        validators.append(ValidatorModel('required'))
    validators.extend(get_validator_models(registry, node.validator))
    return validators


def get_validator_models(
        registry: Registry,
        validator: Optional[ColanderValidator],
) -> Generator[ValidatorModel, Any, None]:
    if validator is None:
        return

    if isfunction(validator):
        adapter_name = f'{validator.__module__}.{validator.__qualname__}'
        validator = _FunctionBasedValidator(validator)
    else:
        adapter_name = ''

    converter: Optional[ValidatorConverter] = registry.queryAdapter(
        validator,
        interfaces.IValidatorConverter,
        name=adapter_name,
    )
    if converter:
        yield from converter(registry, validator)


def add_validator_converter(
        config: Configurator,
        validator_type: Type[ColanderValidator],
        converter: ValidatorConverter,
):
    dotted = config.maybe_dotted
    validator_type = dotted(validator_type)
    converter = dotted(converter)

    if isfunction(validator_type):
        adapter_name = f'{validator_type.__module__}.{validator_type.__qualname__}'
        required = [interfaces.IColanderValidator]
    else:
        adapter_name = ''
        required = [validator_type]

    discriminator = f'restfw_admin_validator:{id(validator_type)}'
    intr = config.introspectable(
        category_name='restfw_admin_validator_converter',
        discriminator=discriminator,
        title=config.object_description(converter),
        type_name='restfw_admin_validator_converter',
    )
    intr['validator_type'] = validator_type
    intr['converter'] = converter

    def register():
        def adapter(_):
            return converter

        config.registry.registerAdapter(
            adapter,
            required,
            provided=interfaces.IValidatorConverter,
            name=adapter_name,
        )

    config.action(discriminator, register, introspectables=(intr,))
    return converter


class validator_converter:

    def __init__(self, validator_type: Type[ColanderValidator], **kwargs):
        self.validator_type = validator_type
        self.depth = kwargs.pop('_depth', 0)
        self.category = kwargs.pop('_category', 'restfw_admin')

    def register(self, scanner, name, wrapped):
        add_validator_converter(
            scanner.config,
            self.validator_type,
            wrapped,
        )

    def __call__(self, wrapped: ValidatorConverter):
        venusian.attach(
            wrapped, self.register, category=self.category,
            depth=self.depth + 1,
        )
        return wrapped


def get_validators_by_name(validators: List[ValidatorModel], name: str) -> List[ValidatorModel]:
    return [v for v in validators if v.name == name]


# Converters

@validator_converter(schemas.NullableValidator)
def nullable_validator(registry: Registry, validator: schemas.NullableValidator):
    # NullableValidator used as part of Nullable node type.
    yield from get_validator_models(registry, validator.validator)


@validator_converter(colander.Range)
def range_validator(registry: Registry, validator: colander.Range):
    if validator.min is not None:
        yield ValidatorModel('min_value', validator.min)
    if validator.max is not None:
        yield ValidatorModel('max_value', validator.max)


@validator_converter(colander.Length)
def length_validator(registry: Registry, validator: colander.Length):
    if validator.min is not None:
        yield ValidatorModel('min_length', validator.min)
    if validator.max is not None:
        yield ValidatorModel('max_length', validator.max)


@validator_converter(colander.Regex)
def regex_validator(registry: Registry, validator: colander.Regex):
    yield ValidatorModel('regex', validator.match_object.pattern)


@validator_converter(colander.Email)
def email_validator(registry: Registry, validator: colander.Email):
    yield ValidatorModel('is_email')


@validator_converter(colander.All)
def all_validator(registry: Registry, validator: colander.All):
    for child_validator in validator.validators:
        yield from get_validator_models(registry, child_validator)


@validator_converter(colander.OneOf)
def one_of_validator(registry: Registry, validator: colander.OneOf):
    yield ValidatorModel('choices', validator.choices)
