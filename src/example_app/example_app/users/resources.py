# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from typing import Literal, Optional

import pendulum
from pyramid.security import Allow, Authenticated, DENY_ALL
from restfw.hal import HalResource, HalResourceWithEmbedded, list_to_embedded_resources
from restfw.interfaces import MethodOptions
from restfw.schemas import GetEmbeddedSchema

from . import schemas


class User(HalResource):
    url_placeholder = '<user_id>'

    def __init__(self, model, parent):
        """
        :type model: dict
        :type parent: Users
        """
        self.model = model
        self.__parent__ = parent
        self.__name__ = str(model['id'])

    options_for_get = MethodOptions(None, schemas.UserSchema,
                                    permission='users.get')

    def as_dict(self, request):
        res = self.model.copy()
        res['created'] = res['created'].isoformat()
        return res

    options_for_patch = MethodOptions(schemas.PatchUserSchema, schemas.UserSchema,
                                      permission='users.edit')

    def http_patch(self, request, params):
        self.model.update(params)
        created = False
        return self, created

    options_for_delete = MethodOptions(None, None, permission='users.edit')

    def http_delete(self, request, params):
        self.__parent__.delete_user(self)


class Users(HalResourceWithEmbedded):

    __acl__ = [
        (Allow, Authenticated, 'users.'),
        DENY_ALL,
    ]

    def __init__(self):
        self._users_list = []
        self._users_dict = {}
        self._next_id = 1

    def __getitem__(self, key):
        user = self._users_dict.get(key)
        if user:
            return user
        return super(Users, self).__getitem__(key)

    options_for_get = MethodOptions(GetEmbeddedSchema, schemas.UsersSchema,
                                    permission='users.get')

    def get_embedded(self, request, params):
        return list_to_embedded_resources(
            request, params,
            resources=self._users_list,
            parent=self,
            embedded_name='users',
        )

    options_for_post = MethodOptions(schemas.CreateUserSchema, schemas.UserSchema,
                                     permission='users.edit')

    def http_post(self, request, params):
        created = True
        resource = self.create_user(**params)
        return resource, created

    def create_user(self, first_name, last_name, age: Optional[int] = None, sex: Literal['m', 'f'] = 'm'):
        user_id = self._next_id
        model = {
            'id': user_id,
            'created': pendulum.now(pendulum.UTC),
            'first_name': first_name,
            'last_name': last_name,
            'age': age,
            'sex': sex,
            'children': [],
        }
        self._next_id += 1
        user = User(model, parent=self)
        self._users_list.append(user)
        self._users_dict[str(user_id)] = user
        return user

    def get_user_by_name(self, first_name):
        for user in self._users_list:
            if user.model['first_name'] == first_name:
                return user

    def delete_user(self, user: User):
        self._users_list.remove(user)
        self._users_dict.pop(str(user.model['id']))


def check_credentials(username, password, request):
    users = request.root['users']  # type: Users
    user = users.get_user_by_name(username)
    if user:
        return [user.model['id']]
