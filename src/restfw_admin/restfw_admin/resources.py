# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
import dataclasses

from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.registry import Registry
from pyramid.request import Request
from pyramid.security import Allow, Everyone
from restfw.hal import HalResource, HalResourceWithEmbedded, SimpleContainer, list_to_embedded_resources
from restfw.interfaces import MethodOptions
from restfw.root import Root

from . import schemas
from .interfaces import IAdminChoices, IResourceAdminFabric
from .models import ApiInfoModel
from .resource_admin import ResourceAdmin


class ApiInfo(HalResource):

    __acl__ = [
        (Allow, Everyone, 'rest_admin.api_info.'),
    ]

    options_for_get = MethodOptions(None, None, permission='rest_admin.api_info.get')

    def as_dict(self, request: Request):
        title = request.registry.settings.get('restfw_admin.title', 'Admin UI')
        root_url = request.registry.settings.get('restfw_admin.root_url', '')
        if not root_url:
            root_url = request.resource_url(request.root)
        model = ApiInfoModel(
            root_url=root_url.rstrip('/'),
            title=title,
            resources=self.get_resources_info(request),
        )
        return dataclasses.asdict(model)

    def get_resources_info(self, request: Request):
        registry: Registry = request.registry
        resources = []
        for name, fabric in registry.getUtilitiesFor(IResourceAdminFabric):
            resource_admin: ResourceAdmin = fabric(request, name)
            info = resource_admin.get_resource_info()
            resources.append((info.index, name, info))
        return {
            name: info
            for _, name, info in sorted(resources)
        }


class AdminChoices(HalResourceWithEmbedded):

    def __getitem__(self, key):
        group = key.split(':', 1)
        if group:
            choices = self.get_choices(self.get_registry(), group)
            for choice in choices:
                if choice['uniq_id'] == key:
                    return choice
        return super(AdminChoices, self).__getitem__(key)

    options_for_get = MethodOptions(schemas.GetAdminChoicesSchema,
                                    schemas.AdminChoicesSchema,
                                    permission='admin_choices.get')

    def get_embedded(self, request, params):
        group = params.get('group')
        choice_ids = params.get('id')
        choices = list(self.get_choices(request.registry, group, choice_ids))
        return list_to_embedded_resources(
            request, params, choices,
            parent=self,
            embedded_name='choices',
        )

    @staticmethod
    def get_choices(registry, group=None, choice_ids=None):
        if group:
            utility = registry.queryUtility(IAdminChoices, name=group)
            if utility:
                utilities = [(group, utility)]
            else:
                utilities = []
        else:
            utilities = list(registry.getUtilitiesFor(IAdminChoices))

        utilities.sort(key=lambda x: x[0])

        choice_ids = set(choice_ids) if choice_ids else None

        for group, utility in utilities:
            for value, title in utility(registry):
                if choice_ids and value not in choice_ids:
                    continue
                yield {
                    'uniq_id': '%s:%s' % (group, value),
                    'group': group,
                    'id': value,
                    'name': title
                }


class Admin(SimpleContainer):

    __acl__ = [
        (Allow, Everyone, 'get'),
    ]

    def __init__(self):
        super().__init__()
        self['choices'] = AdminChoices()
        self['api_info.json'] = ApiInfo()

    def http_get(self, request, params):
        url = request.route_url('admin_ui_ts')
        return HTTPMovedPermanently(location=url)


def get_admin(root: Root) -> Admin:
    registry = root.get_registry()
    prefix = registry.settings['restfw_admin.prefix']
    return root[prefix]


def get_admin_choices(root: Root) -> AdminChoices:
    admin = get_admin(root)
    return admin['choices']
