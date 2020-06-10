# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""


def includeme(config):
    """
    :type config: pyramid.config.Configurator
    """
    from pyramid.authentication import BasicAuthAuthenticationPolicy
    from example_app.users.resources import check_credentials

    authn_policy = BasicAuthAuthenticationPolicy(check_credentials)
    config.set_authentication_policy(authn_policy)

    config.include('restfw')
    config.include('restfw_admin')

    from .resources import Users

    def add_to_root(event):
        users = Users()
        users.create_user('Admin', 'Root', age=39)
        users.create_user('Ivan', 'Petrov', age=25)
        event.root['users'] = users

    from restfw.interfaces import IRootCreated
    config.add_subscriber(add_to_root, IRootCreated)

    from .admin import UsersAdmin
    config.add_resource_admin('users', UsersAdmin)

    from restfw.utils import scan_ignore
    config.scan(ignore=scan_ignore(config.registry))
