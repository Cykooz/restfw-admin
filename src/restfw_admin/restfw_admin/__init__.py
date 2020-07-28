# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from pyramid.config import Configurator


def includeme(config: Configurator):
    config.include('restfw')

    settings = config.get_settings()
    prefix = settings.get('restfw_admin.prefix', 'admin').strip('/')
    settings['restfw_admin.prefix'] = prefix

    from .resources import Admin

    def add_to_root(event):
        root = event.root
        root[prefix] = Admin()

    from restfw.interfaces import IRootCreated
    config.add_subscriber(add_to_root, IRootCreated)

    from .views import admin_ui, redirect_to_admin_ui
    ui_url = f'/{prefix}/ui'
    config.add_route('admin_ui_ts', f'{ui_url}/')
    config.add_view(admin_ui, route_name='admin_ui_ts', request_method='GET')

    config.add_route('admin_ui', ui_url)
    config.add_view(redirect_to_admin_ui, route_name='admin_ui', request_method='GET')

    config.add_route('admin_ui_index', f'{ui_url}/index.html')
    config.add_view(redirect_to_admin_ui, route_name='admin_ui_index', request_method='GET')

    import os
    from pathlib import Path
    admin_ui_dir = Path(__file__).parent / 'admin_ui'
    config.add_static_view(name=ui_url, path=os.fspath(admin_ui_dir))

    import re
    from .config import get_admin_ui_settings
    index_html = (admin_ui_dir / 'index.html').read_text('utf-8')
    index_html_tpl = re.sub(
        r'<script>window\.__RESTFW_ADMIN_PARAMS__.+?</script>',
        '__ADMIN_PARAMS__',
        index_html,
    )
    ui_settings = get_admin_ui_settings(config.registry)
    ui_settings.index_html_tpl = index_html_tpl

    from .config import add_resource_admin
    config.add_directive('add_resource_admin', add_resource_admin)

    from restfw.utils import scan_ignore
    config.scan(ignore=scan_ignore(config.registry))
