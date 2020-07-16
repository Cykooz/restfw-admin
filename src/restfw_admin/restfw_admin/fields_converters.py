# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 10.06.2020
"""
from typing import Dict

import colander
from pyramid.registry import Registry
from restfw import schemas

from . import widgets
from .fields import get_field_widget, get_input_widget, input_field_converter, view_field_converter
from .typing import ColanderNode
from .validators import MaxValue, MinLength, MinValue, Number, Required
from .validators_converters import get_validators, get_validators_by_type


# Boolean

@view_field_converter(colander.Boolean)
def boolean_view(registry: Registry, node: ColanderNode):
    return widgets.BooleanField(
        label=node.title,
    )


@input_field_converter(colander.Boolean)
def boolean_input(registry: Registry, node: ColanderNode):
    return widgets.BooleanInput(
        label=node.title,
        validators=get_validators(registry, node),
    )


# Number

@view_field_converter(colander.Integer)
@view_field_converter(colander.Float)
def number_view(registry: Registry, node: ColanderNode):
    return widgets.NumberField(
        label=node.title,
    )


@input_field_converter(colander.Integer)
@input_field_converter(colander.Float)
def number_input(registry: Registry, node: ColanderNode):
    validators = get_validators(registry, node)
    validators.append(Number())
    params = {}
    if min_validator := get_validators_by_type(validators, MinValue):
        params['min'] = min_validator[0].min
    if max_validator := get_validators_by_type(validators, MaxValue):
        params['max'] = max_validator[0].max
    widget = widgets.NumberInput(
        label=node.title,
        validators=validators,
        **params,
    )
    return widget


# String

@view_field_converter(colander.String)
def string_view(registry: Registry, node: ColanderNode):
    return widgets.TextField(
        label=node.title,
    )


@input_field_converter(colander.String)
def string_input(registry: Registry, node: ColanderNode):
    field = widgets.TextInput(
        label=node.title,
        validators=get_validators(registry, node),
    )
    if not node.typ.allow_empty:
        field.validators.append(MinLength(1))
    return field


# Date

@view_field_converter(colander.Date)
def date_view(registry: Registry, node: ColanderNode):
    return widgets.DateField(
        label=node.title,
    )


@input_field_converter(colander.Date)
def date_input(registry: Registry, node: ColanderNode):
    return widgets.DateInput(
        label=node.title,
        validators=get_validators(registry, node),
    )


# DateTime

@view_field_converter(colander.DateTime)
def datetime_view(registry: Registry, node: ColanderNode):
    return widgets.DateField(
        label=node.title,
        show_time=True,
    )


@input_field_converter(colander.DateTime)
def datetime_input(registry: Registry, node: ColanderNode):
    return widgets.DateTimeInput(
        label=node.title,
        validators=get_validators(registry, node),
    )


# Nullable

@view_field_converter(schemas.Nullable)
def nullable_view(registry: Registry, node: ColanderNode):
    return get_field_widget(registry, node, node.typ.typ)


@input_field_converter(schemas.Nullable)
def nullable_input(registry: Registry, node: ColanderNode):
    widget = get_input_widget(registry, node, node.typ.typ)
    if widget:
        if isinstance(widget, widgets.BooleanInput):
            widget = widgets.NullableBooleanInput(**widget.get_fields())
        else:
            widget.validators = [v for v in widget.validators if not isinstance(v, Required)]
        return widget


# Sequence

@view_field_converter(colander.Sequence)
def sequence_view(registry: Registry, node: ColanderNode):
    fields: Dict[str, widgets.FieldWidget] = {}
    for sub_node in node.children[0].children:
        if widget := get_field_widget(registry, sub_node):
            fields[sub_node.name] = widget
    return widgets.ArrayField(
        label=node.title,
        fields=fields,
    )


@input_field_converter(colander.Sequence)
def sequence_input(registry: Registry, node: ColanderNode):
    fields: Dict[str, widgets.InputWidget] = {}
    for sub_node in node.children[0].children:
        if widget := get_input_widget(registry, sub_node):
            fields[sub_node.name] = widget
    return widgets.ArrayInput(
        label=node.title,
        fields=fields,
        validators=get_validators(registry, node),
    )
