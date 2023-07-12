# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 10.06.2020
"""
from typing import Dict

import colander
from colander import SchemaType
from pyramid.registry import Registry
from restfw import schemas

from . import widgets
from .fields import get_field_widget, get_input_widget, input_field_converter, view_field_converter
from .typing import ColanderNode
from .validators import MinLength, Number, Required
from .validators_converters import get_validators


# Boolean

@view_field_converter(colander.Boolean)
def boolean_field(registry: Registry, node: ColanderNode, node_type: SchemaType):
    return widgets.BooleanField(
        label=node.title,
    )


@input_field_converter(colander.Boolean)
def boolean_input(registry: Registry, node: ColanderNode, node_type: SchemaType):
    return widgets.BooleanInput(
        label=node.title,
        validators=get_validators(registry, node),
    )


# Number

@view_field_converter(colander.Integer)
@view_field_converter(colander.Float)
@view_field_converter(colander.Decimal)
def number_field(registry: Registry, node: ColanderNode, node_type: SchemaType):
    return widgets.NumberField(
        label=node.title,
    )


@input_field_converter(colander.Integer)
@input_field_converter(colander.Float)
@input_field_converter(colander.Decimal)
def number_input(registry: Registry, node: ColanderNode, node_type: SchemaType):
    validators = get_validators(registry, node)
    validators.append(Number())
    widget = widgets.TextInput(
        label=node.title,
        validators=validators,
    )
    return widget


# String

@view_field_converter(colander.String)
def string_field(registry: Registry, node: ColanderNode, node_type: colander.String):
    return widgets.TextField(
        label=node.title,
    )


@input_field_converter(colander.String)
def string_input(registry: Registry, node: ColanderNode, node_type: colander.String):
    field = widgets.TextInput(
        label=node.title,
        validators=get_validators(registry, node),
    )
    if not node_type.allow_empty:
        field.validators.append(MinLength(1))
    return field


# Date

@view_field_converter(colander.Date)
def date_field(registry: Registry, node: ColanderNode, node_type: SchemaType):
    return widgets.DateField(
        label=node.title,
    )


@input_field_converter(colander.Date)
def date_input(registry: Registry, node: ColanderNode, node_type: SchemaType):
    return widgets.DateInput(
        label=node.title,
        validators=get_validators(registry, node),
    )


# DateTime

@view_field_converter(colander.DateTime)
def datetime_field(registry: Registry, node: ColanderNode, node_type: SchemaType):
    return widgets.DateField(
        label=node.title,
        show_time=True,
    )


@input_field_converter(colander.DateTime)
def datetime_input(registry: Registry, node: ColanderNode, node_type: SchemaType):
    return widgets.DateTimeInput(
        label=node.title,
        validators=get_validators(registry, node),
    )


# Nullable

@view_field_converter(schemas.Nullable)
def nullable_field(registry: Registry, node: ColanderNode, node_type: schemas.Nullable):
    return get_field_widget(registry, node, node_type.typ)


@input_field_converter(schemas.Nullable)
def nullable_input(registry: Registry, node: ColanderNode, node_type: schemas.Nullable):
    widget = get_input_widget(registry, node, node_type.typ)
    if widget:
        if isinstance(widget, widgets.BooleanInput):
            widget = widgets.NullableBooleanInput(**widget.get_fields())
        else:
            if isinstance(widget, widgets.SelectInput):
                widget.empty_text = '<none>'
                widget.empty_value = None
            if widget.validators:
                widget.validators = [
                    v
                    for v in widget.validators
                    if not isinstance(v, Required)
                ]
        return widget


# Sequence

@view_field_converter(colander.Sequence)
def sequence_field(registry: Registry, node: ColanderNode, node_type: SchemaType):
    widget = get_field_widget(registry, node.children[0])
    if isinstance(widget, widgets.MappingField):
        return widgets.ArrayField(
            label=node.title,
            fields=widget.fields,
        )
    else:
        return widgets.NestedArrayField(
            label=node.title,
            fields={'': widget},
            single_field=True,
        )


@input_field_converter(colander.Sequence)
def sequence_input(registry: Registry, node: ColanderNode, node_type: SchemaType):
    fields: Dict[str, widgets.InputWidget] = {}
    widget = get_input_widget(registry, node.children[0])
    if isinstance(widget, widgets.MappingInput):
        fields = widget.fields
    else:
        fields[''] = widget
    return widgets.ArrayInput(
        fields=fields,
        label=node.title,
        validators=get_validators(registry, node),
    )


# Mapping

@view_field_converter(colander.Mapping)
def mapping_field(registry: Registry, node: ColanderNode, node_type: colander.Mapping):
    fields: Dict[str, widgets.FieldWidget] = {}
    for sub_node in node.children:
        if widget := get_field_widget(registry, sub_node):
            fields[sub_node.name] = widget
    return widgets.MappingField(
        fields=fields,
        label=node.title,
    )


@input_field_converter(colander.Mapping)
def mapping_input(registry: Registry, node: ColanderNode, node_type: colander.Mapping):
    fields: Dict[str, widgets.InputWidget] = {}
    for sub_node in node.children:
        if widget := get_input_widget(registry, sub_node):
            fields[sub_node.name] = widget
    return widgets.MappingInput(
        fields=fields,
        label=node.title,
    )
