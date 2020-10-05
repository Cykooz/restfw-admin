# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 09.02.2020
"""
from restfw_admin.config import resource_admin_config
from restfw_admin.resource_admin import Exclude, ResourceAdmin, ViewSettings
from restfw_admin import widgets as all_widgets
from .resources import User, Users


@resource_admin_config('users')
class UsersAdmin(ResourceAdmin):
    container = Users
    child = User
    title = 'User'
    location = '/users'
    index = 0
    list_view = ViewSettings(
        fields=Exclude('last_name', 'children', 'current_work')
    )
    edit_view = ViewSettings(
        widgets={
            'current_work': all_widgets.JsonInput(),
        }
    )
