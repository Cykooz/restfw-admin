# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 09.02.2020
"""
from restfw_admin.resource_admin import Exclude, ResourceAdmin, ViewSettings
from .resources import User, Users


class UsersAdmin(ResourceAdmin):
    container = Users
    child = User
    title = 'User'
    location = '/users'
    index = 0
    list_view = ViewSettings(
        fields=Exclude({'last_name', 'children'})
    )
