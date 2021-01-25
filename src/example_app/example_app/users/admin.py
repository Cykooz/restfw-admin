# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 09.02.2020
"""
from restfw_admin.config import resource_admin_config
from restfw_admin.resource_admin import Exclude, ResourceAdmin, ViewSettings
from .views import UserView, UsersView


@resource_admin_config('users')
class UsersAdmin(ResourceAdmin):
    title = 'User'
    container_view_class = UsersView
    child_view_class = UserView
    location = '/users'
    index = 0
    list_view = ViewSettings(
        fields=Exclude('last_name', 'children', 'current_work')
    )
