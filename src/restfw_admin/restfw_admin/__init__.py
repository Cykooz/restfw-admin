# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from pyramid.config import Configurator


def includeme(config: Configurator):
    config.include('restfw')

    from .resources import AdminChoices, ApiInfo

    def add_to_root(event):
        root = event.root
        root['admin_choices'] = AdminChoices()
        root['api_info.json'] = ApiInfo()

    from restfw.interfaces import IRootCreated
    config.add_subscriber(add_to_root, IRootCreated)

    from .config import add_resource_admin
    config.add_directive('add_resource_admin', add_resource_admin)

    import os
    from pathlib import Path
    admin_ui_dir = Path(__file__).parent / '..' / '..' / 'admin_ui' / 'build'
    config.add_static_view(name='admin', path=os.fspath(admin_ui_dir))

    from restfw.utils import scan_ignore
    config.scan(ignore=scan_ignore(config.registry))
