# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 25.04.2020
"""
import dataclasses
from typing import List, Literal, Optional, Set, Type, Union

import colander
from pyramid.registry import Registry
from pyramid.request import Request
from restfw.hal import HalResource

from . import models
from .fields import FieldPredicate, get_input_fields, get_view_fields
from .typing import ColanderNode


@dataclasses.dataclass()
class Only:
    names: Set[str]

    def is_enabled(self, name: str):
        return name in self.names


@dataclasses.dataclass()
class Exclude:
    names: Set[str]

    def is_enabled(self, name: str):
        return name not in self.names


@dataclasses.dataclass()
class ViewSettings:
    fields: Optional[Union[Only, Exclude]] = None


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

        predicate = self._get_field_predicate(view_settings)
        if fields_type == 'input':
            get_fields = get_input_fields
        else:
            get_fields = get_view_fields
        fields = get_fields(self._registry, schema_node, predicate)

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

    def _get_field_predicate(self, view_settings: ViewSettings) -> Optional[FieldPredicate]:
        predicates: List[FieldPredicate] = [
            f.is_enabled
            for f in (self.fields, view_settings.fields)
            if f
        ]
        if not predicates:
            return

        if len(predicates) == 1:
            return predicates[0]

        return lambda x: all(p(x) for p in predicates)
