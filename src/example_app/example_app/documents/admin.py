# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 31.07.2020
"""

from restfw_admin import widgets as all_widgets
from restfw_admin.config import resource_admin_config, admin_choices_config
from restfw_admin.resource_admin import (
    Exclude,
    Only,
    ResourceAdmin,
    ViewSettings,
    ListViewSettings,
    Filters,
)
from restfw_admin.validators import Required
from .views import DocView, DocsView


@admin_choices_config('doc_types')
def get_doc_types(request):
    return [
        ('article', 'Article'),
        ('news', 'News'),
        ('paper', 'Paper'),
    ]


@resource_admin_config('docs')
class DocsAdmin(ResourceAdmin):
    title = 'Documents'
    container_view_class = DocsView
    child_view_class = DocView
    location = '/docs'
    index = 1
    default_fields = Exclude('_embedded')
    fields = Only(
        'id',
        'user_id',
        'name',
        'data',
        'image',
        'publish_date',
        'weight',
        'meta',
    )
    list_view = ListViewSettings(
        fields=Exclude('data', 'image', 'meta.custom'),
        widgets={
            'user_id': all_widgets.ReferenceField(
                reference='users',
                reference_field='first_name',
                label='User',
                link='show',
            ),
            'meta': {
                'type': all_widgets.DynSelectField(group='doc_types'),
            },
        },
        filters=Filters(),
        infinite_pagination=True,
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
            'meta': {
                'type': all_widgets.DynSelectField(group='doc_types'),
            },
        }
    )
    create_view = ViewSettings(
        widgets={
            'user_id': all_widgets.ReferenceInput(
                reference='users',
                option_text='first_name',
                label='User',
                validators=[Required()],
            ),
            'data': all_widgets.RichTextInput(),
            'meta': {
                'type': all_widgets.DynSelectInput(group='doc_types'),
            },
        }
    )
    edit_view = ViewSettings(
        widgets={
            'data': all_widgets.RichTextInput(),
            'meta': {
                'type': all_widgets.DynSelectInput(group='doc_types'),
            },
        }
    )
