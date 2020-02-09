# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
import pytest

from ..interfaces import IAdminReactResources


@pytest.fixture(name='pyramid_apps')
def pyramid_apps_fixture():
    return [
        'mountbit.provisioner.admin',
    ]


@pytest.fixture(name='cleanup_registry', scope='session')
def cleanup_registry_fixture():

    def cleanup(registry):
        """
        :type registry: pyramid.registry.Registry
        """
        for name, utility in list(registry.getUtilitiesFor(IAdminReactResources)):
            registry.unregisterUtility(utility, IAdminReactResources, name=name)

    return cleanup
