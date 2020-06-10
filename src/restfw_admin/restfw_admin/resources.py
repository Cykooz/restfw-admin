# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
import dataclasses

from pyramid.registry import Registry
from pyramid.request import Request
from restfw.hal import HalResource, HalResourceWithEmbedded, list_to_embedded_resources
from restfw.interfaces import MethodOptions

from . import schemas
from .interfaces import IAdminChoices, IResourceAdminFabric
from .models import ApiInfoModel
from .resource_admin import ResourceAdmin


class ApiInfo(HalResource):

    def as_dict(self, request):
        root_url = request.resource_url(request.root).rstrip('/')
        model = ApiInfoModel(
            root_url=root_url,
            title='Admin for Example App',
            resources=self.get_resources_info(request),
        )
        return dataclasses.asdict(model)

    def get_resources_info(self, request: Request):
        registry: Registry = request.registry
        resources = {}
        for name, fabric in registry.getUtilitiesFor(IResourceAdminFabric):
            resource_admin: ResourceAdmin = fabric(request, name)
            resources[name] = resource_admin.get_resource_info()
        return resources


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
