# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 31.07.2020
"""
from restfw_admin.config import resource_admin_config
from restfw_admin.resource_admin import Exclude, ResourceAdmin, ViewSettings
from restfw_admin.validators import Required
from restfw_admin.widgets import ReferenceField, ReferenceInput
from .resources import Doc, Docs


@resource_admin_config('docs')
class DocsAdmin(ResourceAdmin):
    container = Docs
    child = Doc
    title = 'Documents'
    location = '/docs'
    index = 1
    list_view = ViewSettings(
        fields=Exclude('data'),
        widgets={
            'user_id': ReferenceField(
                reference='users',
                reference_field='first_name',
                label='User',
                link='show',
            )
        }
    )
    create_view = ViewSettings(
        widgets={
            'user_id': ReferenceInput(
                reference='users',
                option_text='first_name',
                label='User',
                validators=[Required()]
            )
        }
    )
