# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 25.04.2020
"""
from functools import partial
from typing import Callable, List, Optional, Type

import colander
import venusian
from pyramid.config import Configurator
from pyramid.registry import Registry

from . import interfaces
from .models import FieldModel
from .typing import ColanderNode
from .utils import slug_to_title
from .validators import get_validators, get_validators_by_name


FieldPredicate = Callable[[str], bool]
Converter = Callable[[Registry, ColanderNode, str, Optional[FieldPredicate]], Optional[FieldModel]]


def get_view_fields(registry: Registry, schema: ColanderNode, predicate: Optional[FieldPredicate] = None):
    fields: List[FieldModel] = []
    for sub_node in schema.children:
        field = get_view_field(registry, sub_node, predicate=predicate)
        if field:
            fields.append(field)
    return fields


def get_input_fields(registry: Registry, schema: ColanderNode, predicate: Optional[FieldPredicate] = None):
    fields: List[FieldModel] = []
    for sub_node in schema.children:
        field = get_input_field(registry, sub_node, predicate=predicate)
        if field:
            fields.append(field)
    return fields


def get_view_field(
        registry: Registry,
        node: ColanderNode,
        node_type: Optional[colander.SchemaType] = None,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
) -> Optional[FieldModel]:
    name = node.name
    if parent_name:
        name = f'{parent_name}.{name}'

    if predicate is not None and not predicate(name):
        return

    node_type = node_type or node.typ
    converter: Optional[Converter] = registry.queryAdapter(node_type, interfaces.IViewFieldConverter)
    if converter:
        field = converter(registry, node, name, predicate)
        if field:
            field = _try_convert_to_select_view(registry, field, node)
        return field


def get_input_field(
        registry: Registry,
        node: ColanderNode,
        node_type: Optional[colander.SchemaType] = None,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
) -> Optional[FieldModel]:
    name = node.name
    if parent_name:
        name = f'{parent_name}.{name}'

    if predicate is not None and not predicate(name):
        return

    node_type = node_type or node.typ
    converter: Optional[Converter] = registry.queryAdapter(node_type, interfaces.IInputFieldConverter)
    if converter:
        field = converter(registry, node, name, predicate)
        if field:
            field = _try_convert_to_select_input(field, node)
        return field


def _try_convert_to_select_view(registry: Registry, field: FieldModel, node: ColanderNode) -> FieldModel:
    validators = get_validators(registry, node)
    choices_validators = get_validators_by_name(validators, 'choices')
    if not choices_validators:
        return field

    choices = [
        {'id': choice, 'name': slug_to_title(str(choice))}
        for choice in choices_validators[0].args[0]
    ]
    return FieldModel(
        type='SelectField',
        name=field.name,
        label=field.label,
        props={'choices': choices},
    )


def _try_convert_to_select_input(field: FieldModel, node: ColanderNode) -> FieldModel:
    choices_validators = get_validators_by_name(field.validators, 'choices')
    if not choices_validators:
        return field

    choices = [
        {'id': choice, 'name': slug_to_title(str(choice))}
        for choice in choices_validators[0].args[0]
    ]
    return FieldModel(
        type='SelectInput',
        name=field.name,
        label=field.label,
        validators=get_validators_by_name(field.validators, 'required'),
        props={'choices': choices},
    )


def add_field_converter(
        config: Configurator,
        node_type: Type[colander.SchemaType],
        converter: Converter,
        is_input=False,
):
    dotted = config.maybe_dotted
    node_type = dotted(node_type)
    converter = dotted(converter)

    if is_input:
        field_type = 'input'
        provided = interfaces.IInputFieldConverter
    else:
        field_type = 'view'
        provided = interfaces.IViewFieldConverter

    discriminator = f'restfw_{field_type}_field:{id(node_type)}'
    intr = config.introspectable(
        category_name='restfw_admin_field_converter',
        discriminator=discriminator,
        title=config.object_description(converter),
        type_name=f'restfw_admin_{field_type}_field_converter',
    )
    intr['node_type'] = node_type
    intr['converter'] = converter

    def register():

        def adapter(_):
            return converter

        config.registry.registerAdapter(
            adapter,
            [node_type],
            provided=provided,
        )

    config.action(discriminator, register, introspectables=(intr,))
    return converter


def _field_converter(is_input: bool, node_type: Type[colander.SchemaType], **kwargs):
    def register(scanner, name, wrapped):
        add_field_converter(
            scanner.config,
            node_type,
            wrapped,
            is_input=is_input,
        )

    depth = kwargs.pop('_depth', 0)
    category = kwargs.pop('_category', 'restfw_admin')

    def wrapper(wrapped):
        venusian.attach(
            wrapped, register,
            category=category,
            depth=depth + 1,
        )
        return wrapped

    return wrapper


view_field_converter = partial(_field_converter, False)
input_field_converter = partial(_field_converter, True)
