# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from restfw.hal import HalResourceWithEmbedded, list_to_embedded_resources, HalResource
from restfw.interfaces import MethodOptions

from . import schemas
from .interfaces import IAdminChoices


class ApiInfo(HalResource):

    def as_dict(self, request):
        res = {
          'rootUrl': 'http://localhost:6543',
          'title': 'Admin for Example App',
        }
        cur_index = 0
        resource = {
            'index': cur_index,
            'name': 'users',
            'title': 'User',
            'location': '/users',
            'id_field': 'id',
            'embedded_name': 'users',
            'update_method': 'PATCH',
        }

        return res


class AdminChoices(HalResourceWithEmbedded):

    def __getitem__(self, key):
        group = key.split(':', 1)
        if group:
            choices = self.get_choices(self.get_request(), group)
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
        choices = list(self.get_choices(request, group, choice_ids))
        return list_to_embedded_resources(
            request, params, choices,
            parent=self,
            embedded_name='choices',
        )

    @staticmethod
    def get_choices(request, group=None, choice_ids=None):
        if group:
            utility = request.registry.queryUtility(IAdminChoices, name=group)
            if utility:
                utilities = [(group, utility)]
            else:
                utilities = []
        else:
            utilities = list(request.registry.getUtilitiesFor(IAdminChoices))

        utilities.sort(key=lambda x: x[0])

        choice_ids = set(choice_ids) if choice_ids else None

        for group, utility in utilities:
            for value, title in utility(request):
                if choice_ids and value not in choice_ids:
                    continue
                yield {
                    'uniq_id': '%s:%s' % (group, value),
                    'group': group,
                    'id': value,
                    'name': title
                }
