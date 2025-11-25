# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""


def includeme(config):
    """
    :type config: pyramid.config.Configurator
    """
    from .resources import check_credentials, ChildModel

    from .policy import ExampleSecurityPolicy

    config.set_security_policy(ExampleSecurityPolicy())

    config.include('restfw')
    config.include('restfw_admin')

    from .resources import Users

    def add_to_root(event):
        users = Users()
        users.create_user(
            'Admin',
            'Root',
            age=39,
            current_work={'title': 'Administrator', 'address': 'Yellow st.'},
            children=[
                ChildModel(sex='m', name='Artem', age=13),
                ChildModel(sex='m', name='Andrey', age=22),
            ],
            tags=['admin', 'good employee'],
        )
        users.create_user('Ivan', 'Petrov', age=25)
        event.root['users'] = users

    from restfw.interfaces import IRootCreated

    config.add_subscriber(add_to_root, IRootCreated)

    from pathlib import Path
    from restfw_admin.config import (
        add_restfw_admin_auth_provider,
        add_restfw_admin_http_client,
    )

    static_dir = Path(__file__).parent / 'static'
    auth_provider = static_dir / 'auth_provider.js'
    add_restfw_admin_auth_provider(
        config, 'getBasicAuthProvider', auth_provider.read_text('utf-8')
    )
    http_client = static_dir / 'http_client.js'
    add_restfw_admin_http_client(
        config, 'getHttpClient', http_client.read_text('utf-8')
    )

    from restfw.utils import scan_ignore

    config.scan(ignore=scan_ignore(config.registry))
