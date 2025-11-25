"""
:Authors: cykooz
:Date: 06.07.2023
"""

from pyramid.decorator import reify

from .config import resource_admin_config
from .resource_admin import Only, ResourceAdmin, ViewSettings
from .resources import get_admin_choices
from .views import AdminChoicesView, AdminChoiceView


@resource_admin_config('admin_choices')
class AdminChoicesAdmin(ResourceAdmin):
    title = 'Admin Choices'
    container_view_class = AdminChoicesView
    child_view_class = AdminChoiceView
    id_field: str = 'uniq_id'

    @reify
    def location(self):
        choices = get_admin_choices(self._request.root)
        return self._request.resource_url(choices, app_url='')

    fields = Only(
        'uniq_id',
        'group',
        'id',
        'name',
    )
    list_view = None
    show_view = ViewSettings(
        fields=Only(
            'group',
            'id',
            'name',
        )
    )
