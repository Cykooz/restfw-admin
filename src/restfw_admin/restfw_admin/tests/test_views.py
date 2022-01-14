# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 06.08.2020
"""
import pytest

from ..config import set_restfw_admin_extra_params
from ..resources import get_admin
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


def test_api_info(web_app, pyramid_request):
    api_info = get_admin(pyramid_request.root)['api_info.json']
    url = pyramid_request.resource_url(api_info)
    res = web_app.get(url)
    assert res.json == {
        '_links': {'self': {'href': url}},
        'title': 'Admin UI',
        'root_url': 'http://localhost',
        'resources': {},
        'extra': {},
    }

    # Add extra settings
    set_restfw_admin_extra_params(
        pyramid_request.registry,
        {
            'foo': 123,
            'bar': 'http://admin.go',
        }
    )
    res = web_app.get(url)
    assert res.json == {
        '_links': {'self': {'href': url}},
        'title': 'Admin UI',
        'root_url': 'http://localhost',
        'resources': {},
        'extra': {
            'foo': 123,
            'bar': 'http://admin.go',
        },
    }
