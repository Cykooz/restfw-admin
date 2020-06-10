# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
import pytest


pytest_plugins = [
    'restfw.testing.fixtures',
]


@pytest.fixture(name='pyramid_apps')
def pyramid_apps_fixture():
    return [
        'restfw_admin',
    ]
