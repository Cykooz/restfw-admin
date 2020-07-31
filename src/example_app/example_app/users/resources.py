# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from dataclasses import asdict, dataclass
from typing import Dict, List, Literal, Optional

import pendulum
from pyramid.security import Allow, Authenticated, DENY_ALL, Everyone
from restfw.hal import HalResource, HalResourceWithEmbedded, list_to_embedded_resources
from restfw.interfaces import MethodOptions
from restfw.schemas import GetEmbeddedSchema

from . import schemas


@dataclass()
class ChildModel:
    sex: Literal['m', 'f']
    name: str
    age: Optional[int] = None


@dataclass()
class UserModel:
    id: int
    created: pendulum.DateTime
    first_name: str
    last_name: str
    age: int
    sex: Literal['m', 'f']
    children: List[ChildModel]


class User(HalResource):
    url_placeholder = '<user_id>'

    def __init__(self, model: UserModel, parent: 'Users'):
        self.model = model
        self.__parent__ = parent
        self.__name__ = str(model.id)

    options_for_get = MethodOptions(None, schemas.UserSchema,
                                    permission='users.get')

    def as_dict(self, request):
        res = asdict(self.model)
        res['created'] = res['created'].isoformat()
        return res

    options_for_patch = MethodOptions(schemas.PatchUserSchema, schemas.UserSchema,
                                      permission='users.edit')

    def http_patch(self, request, params: dict):
        for key, value in params.items():
            setattr(self.model, key, value)
        created = False
        return self, created

    options_for_delete = MethodOptions(None, None, permission='users.edit')

    def http_delete(self, request, params):
        self.__parent__.delete_user(self.model.id)


class Users(HalResourceWithEmbedded):

    __acl__ = [
        # (Allow, Authenticated, 'users.'),
        # DENY_ALL,
        (Allow, Everyone, 'users.'),
    ]

    def __init__(self):
        self._models: Dict[str, UserModel] = {}
        self._next_id = 1

    def __getitem__(self, key):
        model = self._models.get(key)
        if model:
            return self.get_user_by_model(model)
        return super().__getitem__(key)

    options_for_get = MethodOptions(GetEmbeddedSchema, schemas.UsersSchema,
                                    permission='users.get')

    def get_embedded(self, request, params):
        users = [self.get_user_by_model(model) for model in self._models.values()]
        return list_to_embedded_resources(
            request, params,
            resources=users,
            parent=self,
            embedded_name='users',
        )

    options_for_post = MethodOptions(schemas.CreateUserSchema, schemas.UserSchema,
                                     permission='users.edit')

    def http_post(self, request, params):
        created = True
        resource = self.create_user(**params)
        return resource, created

    def get_user_by_model(self, model: UserModel):
        return User(model, parent=self)

    def create_user(self, first_name, last_name, age: Optional[int] = None, sex: Literal['m', 'f'] = 'm'):
        user_id = self._next_id
        model = UserModel(
            id=user_id,
            created=pendulum.now(pendulum.UTC),
            first_name=first_name,
            last_name=last_name,
            age=age,
            sex=sex,
            children=[],
        )
        self._next_id += 1
        self._models[str(user_id)] = model
        return self.get_user_by_model(model)

    def get_user_by_name(self, first_name):
        for model in self._models.values():
            if model.first_name == first_name:
                return self.get_user_by_model(model)

    def delete_user(self, user_id: int):
        self._users_dict.pop(str(user_id))


def check_credentials(username, password, request):
    users = request.root['users']  # type: Users
    user = users.get_user_by_name(username)
    if user:
        return [user.model.id]
