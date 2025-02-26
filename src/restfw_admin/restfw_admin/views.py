# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 18.07.2020
"""

import dataclasses

from pyramid.httpexceptions import HTTPMovedPermanently, HTTPOk
from restfw import views
from restfw.interfaces import MethodOptions
from restfw.typing import PyramidRequest

from . import schemas
from .config import get_admin_ui_settings
from .models import ApiInfoModel
from .resources import Admin, AdminChoices, ApiInfo, get_admin, AdminChoice


TEMPLATE = """<script>
{auth_provider}
{http_client}
{upload_provider}
window.__RESTFW_ADMIN_PARAMS__ = {admin_params};
</script>"""


def admin_ui(request: PyramidRequest):
    admin_resource = get_admin(request.root)
    api_info_url = request.resource_url(admin_resource['api_info.json']).rstrip('/')
    admin_params = [f'"apiInfoUrl": "{api_info_url}"']

    auth_provider = http_client = upload_provider = ''
    ui_settings = get_admin_ui_settings(request.registry)
    if ui_settings.auth_provider:
        auth_provider = ui_settings.auth_provider.code
        admin_params.append(f'"getAuthProvider": {ui_settings.auth_provider.name}')
    if ui_settings.http_client:
        http_client = ui_settings.http_client.code
        admin_params.append(f'"getHttpClient": {ui_settings.http_client.name}')
    if ui_settings.upload_provider:
        upload_provider = ui_settings.upload_provider.code
        admin_params.append(
            f'"getFileUploadProvider": {ui_settings.upload_provider.name}'
        )

    admin_params = ','.join(admin_params)
    admin_ui_params = TEMPLATE.format(
        auth_provider=auth_provider,
        http_client=http_client,
        upload_provider=upload_provider,
        admin_params=f'{{{admin_params}}}',
    )
    html = ui_settings.index_html_tpl.replace('__ADMIN_PARAMS__', admin_ui_params)
    response = HTTPOk(content_type='text/html', conditional_response=True)
    response.text = html
    response.md5_etag()
    return response


def redirect_to_admin_ui(request: PyramidRequest):
    url = request.route_url('admin_ui_ts')
    return HTTPMovedPermanently(location=url)


# ApiInfo


@views.resource_view_config()
class ApiInfoView(views.HalResourceView):
    resource: ApiInfo
    options_for_get = MethodOptions(None, None, permission='rest_admin.api_info.get')

    def as_dict(self):
        registry = self.request.registry
        title = registry.settings.get('restfw_admin.title', 'Admin UI')
        root_url = registry.settings.get('restfw_admin.root_url', '')
        extra = registry.get('restfw_admin.extra', {})
        if not root_url:
            root_url = self.request.resource_url(self.request.root)
        model = ApiInfoModel(
            root_url=root_url.rstrip('/'),
            title=title,
            resources=self.resource.get_resources_info(self.request),
            extra=extra,
        )
        return dataclasses.asdict(model)


# AdminChoices


@views.resource_view_config()
class AdminChoiceView(views.ResourceView):
    resource: AdminChoice
    options_for_get = MethodOptions(
        None,
        schemas.AdminChoiceSchema,
        permission='admin_choices.get',
    )

    def as_dict(self):
        return self.resource.model


@views.resource_view_config()
class AdminChoicesView(views.HalResourceWithEmbeddedView):
    resource: AdminChoices
    options_for_get = MethodOptions(
        schemas.GetAdminChoicesSchema,
        schemas.AdminChoicesSchema,
        permission='admin_choices.get',
    )

    def get_embedded(self, params):
        group = params.get('group')
        choice_ids = params.get('id')
        choices = list(
            self.resource.get_choices(self.request.registry, group, choice_ids)
        )
        return views.list_to_embedded_resources(
            self.request,
            params,
            choices,
            parent=self.resource,
            embedded_name='choices',
        )


# Admin


@views.resource_view_config()
class AdminView(views.HalResourceView):
    resource: Admin

    def http_get(self):
        url = self.request.route_url('admin_ui_ts')
        return HTTPMovedPermanently(location=url)
