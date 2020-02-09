# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""


def includeme(config):
    """
    :type config: pyramid.config.Configurator
    """
    config.include('restfw')

    from restfw.interfaces import IRootCreated
    from .resources import AdminChoices

    def add_to_root(event):
        root = event.root
        root['admin_choices'] = AdminChoices()

    config.add_subscriber(add_to_root, IRootCreated)

    from .utils import add_static_admin_react_resource
    config.add_directive('add_static_admin_react_resource', add_static_admin_react_resource)

    from restfw.utils import scan_ignore
    config.scan(ignore=scan_ignore(config.registry))
