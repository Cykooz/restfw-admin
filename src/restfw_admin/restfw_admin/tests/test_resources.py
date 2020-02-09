# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from cykooz.testing import ANY
from mountbit.utils import Enum
from pyramid.httpexceptions import HTTPForbidden, HTTPUnauthorized

from mountbit.provisioner.authentication.interfaces import UserRole
from mountbit.provisioner.users.testing import create_user_with_token
from ..config import admin_choices_config
from ..resources import AdminChoices
from ..utils import get_admin_resource


def test_admin_config(web_app):
    res = web_app.get('admin_resources/admin_config')
    assert res.json == {
        'backend_url': ANY,
    }


@admin_choices_config()
class OrderStatus(Enum):
    running = 'running'
    completed = 'completed'
    canceled = 'canceled'


@admin_choices_config('product_types')
def get_product_types(request):
    return [
        ('contacts', 'Contacts'),
        ('backup', 'Backup'),
        ('family_storage', 'Family Storage'),
    ]


def test_admin_choices(web_app, pyramid_request, app_config):
    admin_choices = get_admin_resource(pyramid_request.root, 'admin_choices')  # type: AdminChoices

    choices = list(admin_choices.get_choices(pyramid_request))
    assert choices == []

    order_status_choices = [
        {
            'uniq_id': 'OrderStatus:canceled', 'group': 'OrderStatus',
            'name': 'Canceled', 'id': 'canceled',
        },
        {
            'uniq_id': 'OrderStatus:completed', 'group': 'OrderStatus',
            'name': 'Completed', 'id': 'completed',
        },
        {
            'uniq_id': 'OrderStatus:running', 'group': 'OrderStatus',
            'name': 'Running', 'id': 'running',
        },
    ]

    product_type_choices = [
        {
            'uniq_id': 'product_types:contacts', 'group': 'product_types',
            'name': 'Contacts', 'id': 'contacts',
        },
        {
            'uniq_id': 'product_types:backup', 'group': 'product_types',
            'name': 'Backup', 'id': 'backup',
        },
        {
            'uniq_id': 'product_types:family_storage', 'group': 'product_types',
            'name': 'Family Storage', 'id': 'family_storage',
        },
    ]

    app_config.scan()
    choices = list(admin_choices.get_choices(pyramid_request))
    assert choices == order_status_choices + product_type_choices

    choices = list(admin_choices.get_choices(pyramid_request, group='OrderStatus'))
    assert choices == order_status_choices

    choices = list(admin_choices.get_choices(pyramid_request, group='product_types'))
    assert choices == product_type_choices

    choices = list(admin_choices.get_choices(pyramid_request, group='unknown'))
    assert choices == []

    choices = list(admin_choices.get_choices(
        pyramid_request, group='OrderStatus', choice_ids=['canceled', 'completed']
    ))
    assert choices == order_status_choices[:2]

    url = pyramid_request.resource_url(admin_choices)
    web_app.get(url, exception=HTTPUnauthorized)

    create_user_with_token('user')
    create_user_with_token('admin', role=UserRole.admin)

    web_app.get(url, auth_token='user', exception=HTTPForbidden)

    res = web_app.get(url, params={'total_count': True}, auth_token='admin')
    assert res.headers['X-Total-Count'] == '6'
    assert res.json == {
        '_links': {
            'self': {'href': url},
        },
        '_embedded': {
            'choices': order_status_choices + product_type_choices
        }
    }

    res = web_app.get(url, params={'total_count': True, 'group': 'OrderStatus'}, auth_token='admin')
    assert res.headers['X-Total-Count'] == '3'
    assert res.json['_embedded']['choices'] == order_status_choices

    res = web_app.get(url, params={'total_count': True, 'group': 'unknown'}, auth_token='admin')
    assert res.headers['X-Total-Count'] == '0'
    assert res.json['_embedded']['choices'] == []
