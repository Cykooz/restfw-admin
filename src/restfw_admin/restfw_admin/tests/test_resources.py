# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from ..config import admin_choices_config
from ..resources import get_admin_choices


@admin_choices_config('product_types')
def get_product_types(request):
    return [
        ('contacts', 'Contacts'),
        ('backup', 'Backup'),
        ('family_storage', 'Family Storage'),
    ]


def test_admin_choices(web_app, pyramid_request, app_config):
    admin_choices = get_admin_choices(pyramid_request.root)
    choices = list(admin_choices.get_choices(pyramid_request.registry))
    assert choices == []

    product_type_choices = [
        {
            'uniq_id': 'product_types:contacts',
            'group': 'product_types',
            'name': 'Contacts',
            'id': 'contacts',
        },
        {
            'uniq_id': 'product_types:backup',
            'group': 'product_types',
            'name': 'Backup',
            'id': 'backup',
        },
        {
            'uniq_id': 'product_types:family_storage',
            'group': 'product_types',
            'name': 'Family Storage',
            'id': 'family_storage',
        },
    ]

    app_config.scan()
    choices = [
        c.model
        for c in admin_choices.get_choices(pyramid_request.registry)
    ]
    assert choices == product_type_choices

    choices = [
        c.model
        for c in admin_choices.get_choices(
            pyramid_request.registry, group='product_types'
        )
    ]
    assert choices == product_type_choices

    choices = [
        c.model
        for c in admin_choices.get_choices(
            pyramid_request.registry, group='unknown'
        )
    ]
    assert choices == []

    # url = pyramid_request.resource_url(admin_choices)
    # web_app.get(url, exception=HTTPUnauthorized)
    #
    # create_user_with_token('user')
    # create_user_with_token('admin', role=UserRole.admin)
    #
    # web_app.get(url, auth_token='user', exception=HTTPForbidden)
    #
    # res = web_app.get(url, params={'total_count': True}, auth_token='admin')
    # assert res.headers['X-Total-Count'] == '6'
    # assert res.json == {
    #     '_links': {
    #         'self': {'href': url},
    #     },
    #     '_embedded': {
    #         'choices': order_status_choices + product_type_choices
    #     }
    # }
    #
    # res = web_app.get(url, params={'total_count': True, 'group': 'OrderStatus'}, auth_token='admin')
    # assert res.headers['X-Total-Count'] == '3'
    # assert res.json['_embedded']['choices'] == order_status_choices
    #
    # res = web_app.get(url, params={'total_count': True, 'group': 'unknown'}, auth_token='admin')
    # assert res.headers['X-Total-Count'] == '0'
    # assert res.json['_embedded']['choices'] == []
