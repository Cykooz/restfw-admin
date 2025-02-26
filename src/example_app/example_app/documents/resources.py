# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 31.07.2020
"""

import decimal
from dataclasses import dataclass, field
from typing import Dict, Optional

import datetime
from pyramid.authorization import Allow, Everyone
from restfw.hal import HalResource


@dataclass()
class DocMetaDataModel:
    type: str = ''
    custom: dict = field(default_factory=dict)


@dataclass()
class File:
    src: str = ''
    title: str = ''


@dataclass()
class DocModel:
    id: int
    user_id: int
    name: str = ''
    data: str = ''
    image: Optional[File] = None
    publish_date: Optional[datetime.datetime] = None
    weight: decimal.Decimal = decimal.Decimal('0.00')
    meta: DocMetaDataModel = field(default_factory=DocMetaDataModel)


class Doc(HalResource):
    url_placeholder = '<doc_id>'

    def __init__(self, model: DocModel, parent: 'Docs'):
        self.model = model
        self.__parent__ = parent
        self.__name__ = str(model.id)

    def http_patch(self, request, params):
        for key, value in params.items():
            if hasattr(self.model, key):
                setattr(self.model, key, value)
        created = False
        return created

    def http_delete(self, request, params):
        self.__parent__.delete_doc(self.model.id)


class Docs(HalResource):
    __acl__ = [
        # (Allow, Authenticated, 'docs.'),
        # DENY_ALL,
        (Allow, Everyone, 'docs.'),
    ]

    def __init__(self):
        self.models: Dict[str, DocModel] = {}
        self._next_id = 1

    def __getitem__(self, key):
        model = self.models.get(key)
        if model:
            return Doc(model, parent=self)
        return super().__getitem__(key)

    def http_post(self, request, params):
        model = DocModel(id=self._next_id, **params)
        self._next_id += 1
        self.models[str(model.id)] = model
        resource = self.get_doc_by_model(model)
        created = True
        return resource, created

    def get_doc_by_model(self, model: DocModel) -> Doc:
        return Doc(model, parent=self)

    def delete_doc(self, doc_id: int):
        self.models.pop(str(doc_id))
