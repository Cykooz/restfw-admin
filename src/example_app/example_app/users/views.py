"""
:Authors: cykooz
:Date: 14.01.2021
"""

from dataclasses import asdict

from restfw import views
from restfw.interfaces import MethodOptions

from . import schemas
from .resources import User, Users


# User


@views.resource_view_config(User)
class UserView(views.HalResourceView):
    resource: User
    options_for_get = MethodOptions(None, schemas.UserSchema, permission='users.get')
    options_for_patch = MethodOptions(
        schemas.PatchUserSchema,
        schemas.UserSchema,
        permission='users.edit',
    )
    options_for_delete = MethodOptions(None, None, permission='users.edit')

    def as_dict(self):
        res = asdict(self.resource.model)
        res['created'] = res['created'].isoformat()
        return res


# Users


@views.resource_view_config(Users)
class UsersView(views.HalResourceWithEmbeddedView):
    resource: Users
    options_for_get = MethodOptions(
        schemas.GetUsersSchema, schemas.UsersSchema, permission='users.get'
    )
    options_for_post = MethodOptions(
        schemas.CreateUserSchema, schemas.UserSchema, permission='users.edit'
    )

    def get_embedded(self, params):
        users = [
            self.resource.get_user_by_model(model)
            for model in self.resource.models.values()
            if _is_conforms_to_filters(model, params)
        ]
        return views.list_to_embedded_resources(
            self.request,
            params,
            resources=users,
            parent=self.resource,
            embedded_name='users',
        )


def _is_conforms_to_filters(model, filters: dict) -> bool:
    id_in = filters.get('id__in', [])
    if id_in and model.id not in id_in:
        return False
    return all(
        not hasattr(model, k) or getattr(model, k) == v for k, v in filters.items()
    )
