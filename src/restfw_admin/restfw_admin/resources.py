# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from typing import TypedDict

from pyramid.authorization import Allow, Everyone
from restfw.hal import HalResource, SimpleContainer
from restfw.root import Root
from restfw.typing import PyramidRequest

from .interfaces import IAdminChoices, IResourceAdminFabric
from .resource_admin import ResourceAdmin


class ApiInfo(HalResource):
    __acl__ = [
        (Allow, Everyone, 'rest_admin.api_info.'),
    ]

    def get_resources_info(self, request: PyramidRequest):
        registry = request.registry
        resources = []
        for name, fabric in registry.getUtilitiesFor(IResourceAdminFabric):
            resource_admin: ResourceAdmin = fabric(request, name)
            info = resource_admin.get_resource_info()
            resources.append(info)
        return {
            info.name: info
            for info in sorted(resources, key=lambda x: x.title)
        }


class ChoiceModel(TypedDict):
    uniq_id: str
    group: str
    id: str
    name: str


class AdminChoice(HalResource):
    url_placeholder = '<choice_id>'

    def __init__(self, model: ChoiceModel, parent: HalResource):
        self.__parent__ = parent
        self.__name__ = model['uniq_id']
        self.model = model


class AdminChoices(HalResource):

    def __getitem__(self, key):
        group = key.split(':', 1)
        if group:
            choices = self.get_choices(self.get_registry(), group)
            for choice in choices:
                if choice.model['uniq_id'] == key:
                    return choice
        return super().__getitem__(key)

    def get_choices(self, registry, group=None, choice_ids=None):
        if group:
            utility = registry.queryUtility(IAdminChoices, name=group)
            if utility:
                utilities = [(group, utility)]
            else:
                utilities = []
        else:
            utilities = list(registry.getUtilitiesFor(IAdminChoices))

        choice_ids = set(choice_ids) if choice_ids else None
        utilities.sort(key=lambda x: x[0])
        for group, utility in utilities:
            for value, title in utility(registry):
                if choice_ids and value not in choice_ids:
                    continue
                yield AdminChoice(
                    model={
                        'uniq_id': f'{group}:{value}',
                        'group': group,
                        'id': value,
                        'name': title
                    },
                    parent=self
                )


class Admin(SimpleContainer):
    __acl__ = [
        (Allow, Everyone, 'get'),
    ]

    def __init__(self):
        super().__init__()
        self['choices'] = AdminChoices()
        self['api_info.json'] = ApiInfo()


def get_admin(root: Root) -> Admin:
    registry = root.get_registry()
    prefix = registry.settings['restfw_admin.prefix']
    return root[prefix]


def get_admin_choices(root: Root) -> AdminChoices:
    admin = get_admin(root)
    return admin['choices']
