# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 10.06.2020
"""
from typing import List, Optional

import colander
from pyramid.registry import Registry
from restfw import schemas

from .fields import (
    FieldPredicate, get_input_field, get_view_field, input_field_converter,
    view_field_converter
)
from .models import FieldModel, ValidatorModel
from .typing import ColanderNode
from .validators import get_validators


# Boolean

@view_field_converter(colander.Boolean)
def boolean_view(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    return FieldModel(
        type='BooleanField',
        name=node.name,
        label=node.title,
    )


@input_field_converter(colander.Boolean)
def boolean_input(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    return FieldModel(
        type='BooleanInput',
        name=node.name,
        label=node.title,
        validators=get_validators(registry, node),
    )


# Number

@view_field_converter(colander.Integer)
@view_field_converter(colander.Float)
def number_view(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    return FieldModel(
        type='NumberField',
        name=node.name,
        label=node.title,
    )


@input_field_converter(colander.Integer)
@input_field_converter(colander.Float)
def number_input(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    field = FieldModel(
        type='NumberInput',
        name=node.name,
        label=node.title,
        validators=get_validators(registry, node),
    )
    field.validators.append(ValidatorModel('is_number'))
    return field


# String

@view_field_converter(colander.String)
def string_view(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    return FieldModel(
        type='TextField',
        name=node.name,
        label=node.title,
    )


@input_field_converter(colander.String)
def string_input(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    field = FieldModel(
        type='TextInput',
        name=node.name,
        label=node.title,
        validators=get_validators(registry, node),
    )
    if not node.typ.allow_empty:
        field.validators.append(ValidatorModel('min_length', 1))
    return field


# Date

@view_field_converter(colander.Date)
def date_view(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    return FieldModel(
        type='DateField',
        name=node.name,
        label=node.title,
    )


@input_field_converter(colander.Date)
def date_input(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    return FieldModel(
        type='DateInput',
        name=node.name,
        label=node.title,
        validators=get_validators(registry, node),
    )


# DateTime

@view_field_converter(colander.DateTime)
def datetime_view(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    return FieldModel(
        type='DateTimeField',
        name=node.name,
        label=node.title,
    )


@input_field_converter(colander.DateTime)
def datetime_input(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    return FieldModel(
        type='DateTimeInput',
        name=node.name,
        label=node.title,
        validators=get_validators(registry, node),
    )


# Nullable

@view_field_converter(schemas.Nullable)
def nullable_view(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    return get_view_field(registry, node, node.typ.typ, parent_name, predicate)


@input_field_converter(schemas.Nullable)
def nullable_input(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    field = get_input_field(registry, node, node.typ.typ, parent_name, predicate)
    if field:
        if field.name == 'BooleanInput':
            field.name = 'NullableBooleanInput'
        else:
            field.validators = [v for v in field.validators if v.name != 'required']
        return field


# Sequence

@view_field_converter(colander.Sequence)
def sequence_view(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    fields: List[FieldModel] = []
    for sub_node in node.children[0].children:
        field = get_view_field(registry, sub_node, parent_name=node.name, predicate=predicate)
        if field:
            field.name = field.name.split('.', 1)[-1]
            fields.append(field)

    return FieldModel(
        type='ArrayField',
        name=node.name,
        label=node.title,
        props={'sub_fields': fields},
    )


@input_field_converter(colander.Sequence)
def sequence_input(
        registry: Registry,
        node: ColanderNode,
        parent_name: str = '',
        predicate: Optional[FieldPredicate] = None,
):
    fields: List[FieldModel] = []
    for sub_node in node.children[0].children:
        field = get_input_field(registry, sub_node, parent_name=node.name, predicate=predicate)
        if field:
            field.name = field.name.split('.', 1)[-1]
            fields.append(field)

    return FieldModel(
        type='ArrayInput',
        name=node.name,
        label=node.title,
        validators=get_validators(registry, node),
        props={'sub_fields': fields},
    )
