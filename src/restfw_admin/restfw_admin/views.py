# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 18.07.2020
"""
from pyramid.httpexceptions import HTTPMovedPermanently, HTTPOk
from pyramid.request import Request

from restfw_admin.config import get_admin_ui_settings


TEMPLATE = '''<script>
{auth_provider}
{http_client}
window.__RESTFW_ADMIN_PARAMS__ = {admin_params};
</script>'''


def admin_ui(request: Request):
    api_info_url = request.resource_url(request.root['admin']['api_info.json']).rstrip('/')
    admin_params = [f'"apiInfoUrl": "{api_info_url}"']

    auth_provider = http_client = ''
    ui_settings = get_admin_ui_settings(request.registry)
    if ui_settings.auth_provider:
        auth_provider = ui_settings.auth_provider.code
        admin_params.append(f'"getAuthProvider": {ui_settings.auth_provider.name}')
    if ui_settings.http_client:
        http_client = ui_settings.http_client.code
        admin_params.append(f'"getHttpClient": {ui_settings.http_client.name}')

    admin_params = ','.join(admin_params)
    admin_ui_params = TEMPLATE.format(
        auth_provider=auth_provider,
        http_client=http_client,
        admin_params=f'{{{admin_params}}}',
    )
    html = ui_settings.index_html_tpl.replace('__ADMIN_PARAMS__', admin_ui_params)
    response = HTTPOk(content_type='text/html', conditional_response=True)
    response.text = html
    response.md5_etag()
    return response


def redirect_to_admin_ui(request: Request):
    url = request.route_url('admin_ui_ts')
    return HTTPMovedPermanently(location=url)
