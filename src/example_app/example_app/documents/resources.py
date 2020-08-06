# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 31.07.2020
"""
from dataclasses import dataclass, asdict
from typing import Dict

from pyramid.security import Allow, Everyone
from restfw.hal import HalResource, HalResourceWithEmbedded, list_to_embedded_resources
from restfw.interfaces import MethodOptions
from restfw.schemas import GetEmbeddedSchema

from . import schemas


@dataclass()
class DocModel:
    id: int
    user_id: int
    data: str = ''


class Doc(HalResource):
    url_placeholder = '<doc_id>'

    def __init__(self, model: DocModel, parent: 'Docs'):
        self.model = model
        self.__parent__ = parent
        self.__name__ = str(model.id)

    options_for_get = MethodOptions(None, schemas.DocSchema, permission='docs.get')

    def as_dict(self, request):
        return asdict(self.model)

    options_for_patch = MethodOptions(schemas.PatchDocSchema, schemas.DocSchema,
                                      permission='docs.edit')

    def http_patch(self, request, params):
        for key, value in params.items():
            if hasattr(self.model, key):
                setattr(self.model, key, value)
        created = False
        return self, created

    options_for_delete = MethodOptions(None, None, permission='docs.edit')

    def http_delete(self, request, params):
        self.__parent__.delete_doc(self.model.id)


class Docs(HalResourceWithEmbedded):

    __acl__ = [
        # (Allow, Authenticated, 'docs.'),
        # DENY_ALL,
        (Allow, Everyone, 'docs.'),
    ]

    def __init__(self):
        self._models: Dict[str, DocModel] = {}
        self._next_id = 1

    def __getitem__(self, key):
        model = self._models.get(key)
        if model:
            return Doc(model, parent=self)
        return super().__getitem__(key)

    options_for_get = MethodOptions(GetEmbeddedSchema, schemas.DocsSchema,
                                    permission='docs.get')

    def get_embedded(self, request, params):
        docs = [self.get_doc_by_model(model) for model in self._models.values()]
        return list_to_embedded_resources(
            request, params, docs,
            parent=self,
            embedded_name='docs',
        )

    options_for_post = MethodOptions(schemas.CreateDocSchema, schemas.DocSchema,
                                     permission='docs.edit')

    def http_post(self, request, params):
        model = DocModel(id=self._next_id, **params)
        self._next_id += 1
        self._models[str(model.id)] = model
        resource = self.get_doc_by_model(model)
        created = True
        return resource, created

    def get_doc_by_model(self, model: DocModel) -> Doc:
        return Doc(model, parent=self)

    def delete_doc(self, doc_id: int):
        self._models.pop(str(doc_id))
