# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 09.02.2020
"""
import colander
from .resources import Users, User


class UsersAdmin(object):
    container = Users
    child = User
    name = 'users'
    title = 'User'
    location = '/users'
    id_field = 'id'
    embedded_name = 'users'
    update_method = 'PATCH'
    index = 0


class AdminResourceInfo(object):
    list_view = None
    show_view = None
    create_view = None
    edit_view = None

    def __init__(self, container, child, id_field='id', embedded_name=None, updated_method='PATCH'):
        options_for_get = container.options_for_get
        if options_for_get and options_for_get.output_schema:
            output_schema = options_for_get.output_schema  # type: colander._SchemaNode

        self.child = child
