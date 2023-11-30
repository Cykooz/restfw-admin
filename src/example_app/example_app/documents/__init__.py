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
        docs.http_post(event.request, params={
            'user_id': 1,
            'name': 'Important document',
            'data': 'It is a document data.'
        })

    from restfw.interfaces import IRootCreated
    config.add_subscriber(add_to_root, IRootCreated)

    from restfw.utils import scan_ignore
    config.scan(ignore=scan_ignore(config.registry))
