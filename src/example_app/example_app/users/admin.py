# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 09.02.2020
"""
from restfw_admin import widgets
from restfw_admin.config import resource_admin_config
from restfw_admin.resource_admin import (
    Only, ResourceAdmin, ListViewSettings, Filters,
    Exclude
)
from .views import UserView, UsersView


@resource_admin_config('users')
class UsersAdmin(ResourceAdmin):
    title = 'User'
    container_view_class = UsersView
    child_view_class = UserView
    location = '/users'
    index = 0
    list_view = ListViewSettings(
        fields=Only(
            'id',
            'created',
            'first_name',
            'age',
            'sex',
            'current_work.title',
            'children.name',
            'tags',
        ),
        widgets={
            'children': {
                'name': widgets.TextField(label='Child names')
            },
            'current_work': {
                'title': widgets.TextField(label='Current work title')
            }
        },
        filters=Filters(
            fields=Exclude('id__in'),
            always_on=['id'],
        ),
    )
