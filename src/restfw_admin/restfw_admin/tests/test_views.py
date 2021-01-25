# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 06.08.2020
"""
import pytest

from ..views import admin_ui


@pytest.fixture(name='pyramid_settings', scope='session')
def pyramid_settings_fixture():
    return {
        'restfw_admin.prefix': 'backend_admin',
    }


def test_admin_ui(pyramid_request):
    res = admin_ui(pyramid_request)
    expect = 'window.__RESTFW_ADMIN_PARAMS__ = {"apiInfoUrl": "http://localhost/backend_admin/api_info.json"}'
    assert expect in res.text
