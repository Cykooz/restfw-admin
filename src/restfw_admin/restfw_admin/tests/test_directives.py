# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from pyramid.threadlocal import get_current_request
from restfw.hal import SimpleContainer

from ..interfaces import IAdminReactResources
from ..utils import set_default_admin_resource


def test_add_static_admin_react_resource(app_config):
    # type: (pyramid.config.Configurator) -> None
    app_config.include('mountbit.provisioner.admin')
    app_config.add_static_admin_react_resource(
        name='testing1',
        asset_spec='mountbit.provisioner.admin.tests:static/admin/resource1.js'
    )
    admin_resources = app_config.registry.getUtility(IAdminReactResources)
    fabrics = dict(admin_resources.sorted())
    assert 'testing1' in fabrics
    request = get_current_request()
    js_code = fabrics['testing1'](request)
    assert js_code.startswith(u'var test = "Проверка 1";')

    app_config.add_static_admin_react_resource(
        name='testing2',
        asset_spec='mountbit.provisioner.admin.tests:static/admin/resource2.js',
        before='testing1',
    )
    admin_resources = app_config.registry.getUtility(IAdminReactResources)
    names = [name for name, _ in admin_resources.sorted()]
    assert names == ['testing2', 'testing1']

    app_config.add_static_admin_react_resource(
        name='testing3',
        asset_spec='mountbit.provisioner.admin.tests:static/admin/resource3.js',
        after='testing2',
    )
    admin_resources = app_config.registry.getUtility(IAdminReactResources)
    names = [name for name, _ in admin_resources.sorted()]
    assert names == ['testing2', 'testing3', 'testing1']


def test_set_default_admin_resource(app_config, pyramid_request):
    app_config.include('mountbit.provisioner.admin')
    root = pyramid_request.root

    key = 'simple'
    api_version = 0
    first_container = SimpleContainer()
    second_container = SimpleContainer()

    resource = set_default_admin_resource(root, key, first_container, api_version)
    assert resource is first_container

    resource = set_default_admin_resource(root, key, second_container, api_version)
    assert resource is first_container
