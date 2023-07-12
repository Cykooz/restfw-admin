# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 25.04.2020
"""
import dataclasses
from typing import Dict, Iterable, List, Literal, Optional, Tuple, Type, Union

import colander
from restfw.typing import PyramidRequest
from restfw.views import HalResourceView

from . import models
from .fields import get_field_widgets, get_input_widgets
from .models import FieldModel
from .typing import ColanderNode
from .widgets import ArrayField, MappingField, NestedArrayField, Widget


@dataclasses.dataclass()
class Only:
    names: Tuple[str, ...]

    def __init__(self, first_name: str, *other_names: str):
        self.names = (first_name,) + other_names


@dataclasses.dataclass()
class Exclude:
    names: Tuple[str, ...]

    def __init__(self, first_name: str, *other_names: str):
        self.names = (first_name,) + other_names


WidgetReplaces = Dict[str, Union[None, Widget, 'WidgetReplaces']]


@dataclasses.dataclass()
class ViewSettings:
    fields: Optional[Union[Only, Exclude]] = None
    widgets: WidgetReplaces = dataclasses.field(default_factory=dict)


@dataclasses.dataclass()
class Filters:
    fields: Optional[Union[Only, Exclude]] = None
    always_on: Optional[Union[List[str], Tuple[str, ...]]] = None
    widgets: WidgetReplaces = dataclasses.field(default_factory=dict)


@dataclasses.dataclass()
class ListViewSettings(ViewSettings):
    filters: Optional[Filters] = None


class ResourceAdmin:
    title: str
    container_view_class: Type[HalResourceView]
    child_view_class: Optional[Type[HalResourceView]] = None
    location: str = ''
    id_field: str = 'id'
    embedded_name: str = ''
    update_method: str = ''
    index: int = 0
    order_by: Optional[list[str]] = None
    default_fields: Optional[Union[Only, Exclude]] = Exclude(
        '_links',
        '_embedded',
    )
    fields: Optional[Union[Only, Exclude]] = None
    list_view: Optional[ListViewSettings] = ListViewSettings()
    show_view = ViewSettings()
    create_view = ViewSettings()
    edit_view = ViewSettings()

    def __init__(self, request: PyramidRequest, name: str):
        self._request = request
        self._registry = request.registry
        self._name = name
        if not self.location:
            self.location = f'/{name}'  # TODO: url-encode

        if not self.embedded_name:
            schema: ColanderNode = self.container_view_class.options_for_get.output_schema()
            for node in schema.children:
                if node.name == '_embedded' and node.children:
                    self.embedded_name = node.children[0].name
                    break
            else:
                self.embedded_name = name

        if not self.update_method and self.child_view_class:
            if self.child_view_class.options_for_patch:
                self.update_method = 'patch'
            elif self.child_view_class.options_for_put:
                self.update_method = 'put'

    def get_resource_info(self) -> models.ResourceInfoModel:
        views = models.ViewsModel(
            list=self.get_list_view(),
            show=self.get_show_view(),
            create=self.get_create_view(),
            edit=self.get_edit_view(),
        )
        deletable = self.child_view_class.options_for_delete is not None
        return models.ResourceInfoModel(
            index=self.index,
            name=self._name,
            title=self.title,
            location=self.location,
            id_field=self.id_field,
            embedded_name=self.embedded_name,
            update_method=self.update_method.upper(),
            deletable=deletable,
            order_by=self.order_by or [],
            views=views,
        )

    def get_list_view(self) -> Optional[models.ListViewModel]:
        if self.list_view is None:
            return
        options_for_get = self.container_view_class.options_for_get
        if options_for_get and options_for_get.output_schema:
            schema: ColanderNode = options_for_get.output_schema()
            embedded_node: Optional[ColanderNode] = schema.get('_embedded')
            if not embedded_node:
                return
            embedded_item_node: Optional[ColanderNode] = embedded_node.get(self.embedded_name)
            if embedded_item_node and isinstance(embedded_item_node.typ, colander.Sequence):
                list_item_node = embedded_item_node.children[0]
                list_view = self._get_view(
                    list_item_node,
                    self.list_view,
                    models.ListViewModel,
                    fields_type='view',
                    use_nested_array_field=True,
                )
                if list_view and self.list_view.filters:
                    filters = self.list_view.filters
                    input_schema: ColanderNode = options_for_get.input_schema()
                    if input_schema:
                        filters_widgets = get_input_widgets(self._registry, input_schema)
                        for widget in filters_widgets.values():
                            widget.helper_text = None
                        list_view.filters = self._widgets_to_fields(
                            ViewSettings(
                                fields=filters.fields,
                                widgets=filters.widgets,
                            ),
                            filters_widgets,
                            use_nested_array_field=True,
                            default_fields=Exclude(
                                'embedded',
                                'offset',
                                'limit',
                                'total_count',
                                'total_count',
                            ),
                            fields=[],
                        )
                        if filters.always_on:
                            for field in list_view.filters:
                                if field.source in filters.always_on:
                                    field.params['alwaysOn'] = True
                return list_view

    def get_show_view(self) -> Optional[models.ShowViewModel]:
        return self._get_view(
            self._get_schema_node(
                self.child_view_class,
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
                self.container_view_class,
                method='post',
                schema_type='input',
            ),
            self.create_view,
            models.CreateViewModel,
            fields_type='input',
        )

    def get_edit_view(self) -> Optional[models.EditViewModel]:
        if self.update_method:
            return self._get_view(
                self._get_schema_node(
                    self.child_view_class,
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
            use_nested_array_field=False,
    ) -> Optional[models.ViewModelType]:
        if schema_node is None:
            return

        if fields_type == 'input':
            get_widgets = get_input_widgets
        else:
            get_widgets = get_field_widgets
        widgets = get_widgets(self._registry, schema_node)
        fields = self._widgets_to_fields(
            view_settings,
            widgets,
            use_nested_array_field,
        )
        return view_model_class(fields=fields)

    def _get_schema_node(
            self,
            view_class: Type[HalResourceView],
            *,
            method: str,
            schema_type: Literal['input', 'output'],
    ) -> Optional[ColanderNode]:
        method_options = getattr(view_class, f'options_for_{method}')
        if not method_options:
            return
        schema_class: Type[ColanderNode] = getattr(
            method_options,
            f'{schema_type}_schema'
        )
        if schema_class:
            return schema_class()

    def _widgets_to_fields(
            self,
            view_settings: ViewSettings,
            widgets: Dict[str, Widget],
            use_nested_array_field=False,
            default_fields=None,
            fields=None,
    ) -> List[FieldModel]:
        default_fields = default_fields if default_fields is not None else self.default_fields
        fields = fields if fields is not None else self.fields
        only_field_names: list[str] = []
        for fields in (default_fields, fields, view_settings.fields):
            if fields:
                names = unflat(fields.names)
                if isinstance(fields, Only):
                    widgets = only_widgets(widgets, names)
                    only_field_names.extend(fields.names)
                elif isinstance(fields, Exclude):
                    widgets = exclude_widgets(widgets, names)
        if view_settings.widgets:
            replace_widgets(widgets, view_settings.widgets)
        if only_field_names:
            filtered_widgets = {}
            for name in only_field_names:
                in_array_field = False
                widget = None
                cur_widgets = widgets
                for sub_name in name.split('.'):
                    if cur_widgets is None:
                        break
                    if isinstance(widget, ArrayField):
                        in_array_field = True
                    widget = cur_widgets.get(sub_name, None)
                    if widget is None:
                        break
                    cur_widgets = getattr(widget, 'fields', None)
                else:
                    if widget is not None:
                        if in_array_field and use_nested_array_field:
                            if isinstance(widget, MappingField):
                                widget = NestedArrayField(
                                    label=widget.label,
                                    fields=widget.fields,
                                )
                            elif isinstance(widget, ArrayField):
                                widget = NestedArrayField(
                                    label=widget.label,
                                    fields=widget.fields,
                                )
                            elif isinstance(widget, NestedArrayField):
                                pass
                            else:
                                widget = NestedArrayField(
                                    label=widget.label,
                                    fields={'': widget},
                                    single_field=True,
                                )
                        filtered_widgets[name] = widget
            widgets = filtered_widgets
        return [
            widget.to_model(name)
            for name, widget in widgets.items()
        ]


def unflat(names: Iterable[str]) -> Dict[str, dict]:
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


def replace_widgets(widgets: Dict[str, Widget], replaces: WidgetReplaces):
    """Replace widgets inplace."""
    for name, value in replaces.items():
        if name not in widgets:
            continue
        if value is None:
            del widgets[name]
        elif isinstance(value, Widget):
            widgets[name] = value
        elif isinstance(value, dict):
            current_widget = widgets[name]
            if hasattr(current_widget, 'fields'):
                replace_widgets(current_widget.fields, value)
