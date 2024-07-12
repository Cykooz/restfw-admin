# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 31.07.2020
"""

from pyramid.config import Configurator


def includeme(config: Configurator):
    config.include('restfw')
    config.include('restfw_admin')
    config.include('example_app.users')

    from .resources import Docs

    def add_to_root(event):
        docs = event.root['docs'] = Docs()
        for i in range(1, 1001):
            docs.http_post(
                event.request,
                params={
                    'user_id': 1,
                    'name': f'Important document {i}',
                    'data': f'It is a data of document {i}.',
                },
            )

    from restfw.interfaces import IRootCreated

    config.add_subscriber(add_to_root, IRootCreated)

    from restfw.utils import scan_ignore

    config.scan(ignore=scan_ignore(config.registry))
