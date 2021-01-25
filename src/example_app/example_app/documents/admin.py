# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 31.07.2020
"""
from restfw_admin import widgets as all_widgets
from restfw_admin.config import resource_admin_config
from restfw_admin.resource_admin import Exclude, ResourceAdmin, ViewSettings
from restfw_admin.validators import Required
from .views import DocView, DocsView


@resource_admin_config('docs')
class DocsAdmin(ResourceAdmin):
    title = 'Documents'
    container_view_class = DocsView
    child_view_class = DocView
    location = '/docs'
    index = 1
    list_view = ViewSettings(
        fields=Exclude('data'),
        widgets={
            'user_id': all_widgets.ReferenceField(
                reference='users',
                reference_field='first_name',
                label='User',
                link='show',
            )
        }
    )
    show_view = ViewSettings(
        widgets={
            'user_id': all_widgets.ReferenceField(
                reference='users',
                reference_field='first_name',
                label='User',
                link='show',
            ),
            'data': all_widgets.RichTextField(),
        }
    )
    create_view = ViewSettings(
        widgets={
            'user_id': all_widgets.ReferenceInput(
                reference='users',
                option_text='first_name',
                label='User',
                validators=[Required()]
            ),
            'data': all_widgets.RichTextInput(),
        }
    )
    edit_view = ViewSettings(
        widgets={
            'data': all_widgets.RichTextInput(),
        }
    )
