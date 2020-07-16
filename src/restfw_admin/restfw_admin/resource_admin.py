# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 25.04.2020
"""
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Sequence, Tuple, Type, Union

import colander
from pyramid.registry import Registry
from pyramid.request import Request
from restfw.hal import HalResource

from . import models
from .fields import get_field_widgets, get_input_widgets
from .models import FieldModel
from .typing import ColanderNode
from .widgets import Widget


@dataclass()
class Only:
    names: Tuple[str, ...]

    def __init__(self, *args: str):
        self.names = args


@dataclass()
class Exclude:
    names: Tuple[str, ...]

    def __init__(self, *args: str):
        self.names = args


@dataclass()
class ViewSettings:
    fields: Optional[Union[Only, Exclude]] = None
    widgets: Dict[str, Widget] = field(default_factory=dict)


class ResourceAdmin:
    container: Type[HalResource]
    child: Optional[Type[HalResource]] = None
    title: str = ''
    location: str = ''
    id_field: str = 'id'
    embedded_name: str = ''
    update_method: str = ''
    index: int = 0
    fields: Optional[Union[Only, Exclude]] = None
    list_view = ViewSettings()
    show_view = ViewSettings()
    create_view = ViewSettings()
    edit_view = ViewSettings()

    def __init__(self, request: Request, name: str):
        self._request = request
        self._registry: Registry = request.registry
        self._name = name
        if not self.title:
            self.title = self.container.__name__
        if not self.location:
            self.location = f'/{name}'  # TODO: url-encode

        if not self.embedded_name:
            schema: ColanderNode = self.container.options_for_get.output_schema()
            for node in schema.children:
                if node.name == '_embedded' and node.children:
                    self.embedded_name = node.children[0].name
                    break
            else:
                self.embedded_name = name

        if not self.update_method and self.child:
            if self.child.options_for_patch:
                self.update_method = 'patch'
            elif self.child.options_for_put:
                self.update_method = 'put'

    def get_resource_info(self) -> models.ResourceInfoModel:
        views = models.ViewsModel(
            list=self.get_list_view(),
            show=self.get_show_view(),
            create=self.get_create_view(),
            edit=self.get_edit_view(),
        )
        deletable = self.child.options_for_delete is not None
        return models.ResourceInfoModel(
            index=self.index,
            name=self._name,
            title=self.title,
            location=self.location,
            id_field=self.id_field,
            embedded_name=self.embedded_name,
            update_method=self.update_method.upper(),
            deletable=deletable,
            views=views,
        )

    def get_list_view(self) -> Optional[models.ListViewModel]:
        options_for_get = self.container.options_for_get
        if options_for_get and options_for_get.output_schema:
            schema: ColanderNode = options_for_get.output_schema()
            embedded_node: Optional[ColanderNode] = schema.get('_embedded')
            if not embedded_node:
                return
            embedded_item_node: Optional[ColanderNode] = embedded_node.get(self.embedded_name)
            if embedded_item_node and isinstance(embedded_item_node.typ, colander.Sequence):
                list_item_node = embedded_item_node.children[0]
                return self._get_view(
                    list_item_node,
                    self.list_view,
                    models.ListViewModel,
                    fields_type='view',
                )

    def get_show_view(self) -> Optional[models.ShowViewModel]:
        return self._get_view(
            self._get_schema_node(
                self.child,
                method='get',
                schema_type='output',
            ),
            self.show_view,
            models.ShowViewModel,
            fields_type='view',
        )

    def get_create_view(self) -> Optional[models.CreateViewModel]:
        return self._get_view(
            self._get_schema_node(
                self.container,
                method='post',
                schema_type='input',
            ),
            self.create_view,
            models.CreateViewModel,
            fields_type='input',
        )

    def get_edit_view(self) -> Optional[models.EditViewModel]:
        return self._get_view(
            self._get_schema_node(
                self.child,
                method=self.update_method,
                schema_type='input',
            ),
            self.edit_view,
            models.EditViewModel,
            fields_type='input',
        )

    def _get_view(
            self,
            schema_node: Optional[ColanderNode],
            view_settings: ViewSettings,
            view_model_class: Type[models.ViewModelType],
            *,
            fields_type: Literal['view', 'input'],
    ) -> Optional[models.ViewModelType]:
        if schema_node is None:
            return

        if fields_type == 'input':
            get_fields = get_input_widgets
        else:
            get_fields = get_field_widgets
        widgets = get_fields(self._registry, schema_node)
        fields = self._widgets_to_fields(view_settings, widgets)
        return view_model_class(fields=fields)

    def _get_schema_node(
            self,
            resource_class: Type[HalResource],
            *,
            method: str,
            schema_type: Literal['input', 'output'],
    ) -> Optional[ColanderNode]:
        method_options = getattr(resource_class, f'options_for_{method}')
        if not method_options:
            return
        schema_class: Type[ColanderNode] = getattr(
            method_options,
            f'{schema_type}_schema'
        )
        if schema_class:
            return schema_class()

    def _widgets_to_fields(self, view_settings: ViewSettings, widgets: Dict[str, Widget]) -> List[FieldModel]:
        for fields in (self.fields, view_settings.fields):
            if fields:
                names = unflat(fields.names)
                if isinstance(fields, Only):
                    widgets = only_widgets(widgets, names)
                elif isinstance(fields, Exclude):
                    widgets = exclude_widgets(widgets, names)
        return [
            widget.to_model(name)
            for name, widget in widgets.items()
        ]


def unflat(names: Sequence[str]) -> Dict[str, dict]:
    """Convert a sequence of doted names into a dictionary.

    >>> unflat(['name', 'child.name', 'child.age', 'child', 'parent.work.name'])
    {'name': {}, 'child': {'name': {}, 'age': {}}, 'parent': {'work': {'name': {}}}}
    """
    fields = {}
    for name in names:
        inner_fields = fields
        while name:
            prefix, _, name = name.partition('.')
            inner_fields = inner_fields.setdefault(prefix, {})
    return fields


def only_widgets(widgets: Dict[str, Widget], names: Dict[str, dict]) -> Dict[str, Widget]:
    """Returns a dictionary with widgets whose name is contained in "names" dictionary."""
    res = {}
    for name, inner_names in names.items():
        widget = widgets.get(name)
        if not widget:
            continue
        if inner_names and hasattr(widget, 'fields'):
            widget.fields = only_widgets(widget.fields, inner_names)
        res[name] = widget
    return res


def exclude_widgets(widgets: Dict[str, Widget], names: Dict[str, dict]) -> Dict[str, Widget]:
    """Returns a dictionary without widgets whose name is contained in "names" dictionary."""
    widgets = widgets.copy()
    for name, inner_names in names.items():
        if inner_names:
            widget = widgets.get(name)
            if widget and hasattr(widget, 'fields'):
                widget.fields = exclude_widgets(widget.fields, inner_names)
        else:
            widgets.pop(name, None)
    return widgets
