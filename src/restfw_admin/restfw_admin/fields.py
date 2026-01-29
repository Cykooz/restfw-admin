# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 25.04.2020
"""

import copy
from functools import partial
from typing import Callable, Dict, Optional, Type

import colander
import venusian
from pyramid.config import Configurator
from pyramid.registry import Registry

from . import interfaces
from .typing import ColanderNode
from .utils import slug_to_title
from .validators import Choices, Required
from .validators_converters import get_validators, get_validators_by_type
from .widgets import FieldWidget, InputWidget, SelectField, SelectInput, WidgetOptions


FieldConverter = Callable[
    [Registry, ColanderNode, colander.SchemaType], Optional[FieldWidget]
]
InputConverter = Callable[
    [Registry, ColanderNode, colander.SchemaType], Optional[InputWidget]
]


def get_field_widgets(registry: Registry, schema: ColanderNode):
    widgets: Dict[str, FieldWidget] = {}
    for sub_node in schema.children:
        widget = get_field_widget(registry, sub_node)
        if widget:
            widgets[sub_node.name] = widget
    return widgets


def get_input_widgets(registry: Registry, schema: ColanderNode):
    widgets: Dict[str, InputWidget] = {}
    for sub_node in schema.children:
        widget = get_input_widget(registry, sub_node)
        if widget:
            widgets[sub_node.name] = widget
    return widgets


def get_field_widget(
    registry: Registry,
    node: ColanderNode,
    node_type: Optional[colander.SchemaType] = None,
) -> Optional[FieldWidget]:
    widget = None
    node_type = node_type or node.typ
    converter: Optional[FieldConverter] = registry.queryAdapter(
        node_type, interfaces.ISchemaNodeToFieldWidget
    )
    if converter:
        widget = converter(registry, node, node_type)

    if user_widgets := node.widget:
        # Try to find field widget in widgets from colander's node
        if not isinstance(user_widgets, (list, tuple, set)):
            user_widgets = (user_widgets,)
        user_widget: FieldWidget
        for user_widget in user_widgets:
            if isinstance(user_widget, FieldWidget):
                user_widget = copy.deepcopy(user_widget)
                if widget and not user_widget.label:
                    user_widget.label = widget.label
                widget = user_widget
                break

    if widget:
        widget = _try_convert_to_select_field(registry, widget, node)
    return widget


def get_input_widget(
    registry: Registry,
    node: ColanderNode,
    node_type: Optional[colander.SchemaType] = None,
) -> Optional[InputWidget]:
    widget = None
    node_type = node_type or node.typ
    converter: Optional[InputConverter] = registry.queryAdapter(
        node_type, interfaces.ISchemaNodeToInputWidget
    )
    if converter:
        widget = converter(registry, node, node_type)
        if not any(
            node.missing is v
            for v in (
                colander.drop,
                colander.null,
                colander.required,
            )
        ):
            widget.default_value = node.missing

    if user_widgets := node.widget:
        # Try to find input widget in widgets from colander's node
        if not isinstance(user_widgets, (list, tuple, set)):
            user_widgets = (user_widgets,)
        user_widget: InputWidget
        for user_widget in user_widgets:
            if isinstance(user_widget, InputWidget):
                user_widget = copy.deepcopy(user_widget)
                if widget:
                    for name in ('label', 'helper_text', 'default_value'):
                        if not getattr(user_widget, name):
                            setattr(user_widget, name, getattr(widget, name))
                    if user_widget.validators is None:
                        user_widget.validators = widget.validators
                widget = user_widget
                break

    if widget:
        widget = _try_convert_to_select_input(registry, widget, node)
    return widget


def _try_convert_to_select_field(
    registry: Registry, widget: FieldWidget, node: ColanderNode
) -> FieldWidget:
    if isinstance(widget, SelectField):
        return widget

    validators = get_validators(registry, node)
    choices_validators = get_validators_by_type(validators, Choices)
    if not choices_validators:
        return widget

    choices = choices_validators[0].choices
    widget_options: WidgetOptions = getattr(node, 'widget_options', WidgetOptions())
    if widget_options.slug_to_title:
        choices = [(choice, slug_to_title(str(choice))) for choice in choices]

    return SelectField(choices=choices, **widget.get_fields())


def _try_convert_to_select_input(
    registry: Registry, widget: InputWidget, node: ColanderNode
) -> InputWidget:
    if isinstance(widget, SelectInput):
        return widget

    validators = get_validators(registry, node)
    choices_validators = get_validators_by_type(validators, Choices)
    if not choices_validators:
        return widget

    choices = choices_validators[0].choices
    widget_options: WidgetOptions = getattr(node, 'widget_options', WidgetOptions())
    if widget_options.slug_to_title:
        choices = [(choice, slug_to_title(str(choice))) for choice in choices]

    params = widget.get_fields()
    params['validators'] = get_validators_by_type(validators, Required)
    return SelectInput(choices=choices, **params)


def add_field_converter(
    config: Configurator,
    node_type: Type[colander.SchemaType],
    converter: FieldConverter,
    is_input=False,
):
    dotted = config.maybe_dotted
    node_type = dotted(node_type)
    converter = dotted(converter)

    if is_input:
        field_type = 'input'
        provided = interfaces.ISchemaNodeToInputWidget
    else:
        field_type = 'view'
        provided = interfaces.ISchemaNodeToFieldWidget

    discriminator = f'restfw_{field_type}_field:{id(node_type)}'
    intr = config.introspectable(
        category_name='restfw-admin field converters',
        discriminator=discriminator,
        title=config.object_description(converter),
        type_name=f'{field_type} field converter',
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
    category = kwargs.pop('_category', 'pyramid')

    def wrapper(wrapped):
        venusian.attach(
            wrapped,
            register,
            category=category,
            depth=depth + 1,
        )
        return wrapped

    return wrapper


view_field_converter = partial(_field_converter, False)
input_field_converter = partial(_field_converter, True)
