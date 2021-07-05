# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Union

import pendulum
from pyramid.security import Allow, Everyone
from restfw.hal import HalResource


@dataclass()
class ChildModel:
    sex: Literal['m', 'f']
    name: str
    age: Optional[int] = None


@dataclass()
class WorkModel:
    title: str
    address: str


@dataclass()
class UserModel:
    id: int
    created: pendulum.DateTime
    first_name: str
    last_name: str
    age: int
    sex: Optional[Literal['m', 'f']]
    children: List[ChildModel]
    current_work: WorkModel


class User(HalResource):
    url_placeholder = '<user_id>'

    def __init__(self, model: UserModel, parent: 'Users'):
        self.model = model
        self.__parent__ = parent
        self.__name__ = str(model.id)

    def http_patch(self, request, params: dict):
        for key, value in params.items():
            setattr(self.model, key, value)
        created = False
        return created

    def http_delete(self, request, params):
        self.__parent__.delete_user(self.model.id)


class Users(HalResource):
    __acl__ = [
        # (Allow, Authenticated, 'users.'),
        # DENY_ALL,
        (Allow, Everyone, 'users.'),
    ]

    def __init__(self):
        self.models: Dict[str, UserModel] = {}
        self._next_id = 1

    def __getitem__(self, key):
        model = self.models.get(key)
        if model:
            return self.get_user_by_model(model)
        return super().__getitem__(key)

    def http_post(self, request, params):
        created = True
        resource = self.create_user(**params)
        return resource, created

    def get_user_by_model(self, model: UserModel):
        return User(model, parent=self)

    def create_user(self, first_name, last_name, age: Optional[int] = None, sex: Optional[Literal['m', 'f']] = 'm',
                    children=None, current_work: Union[None, dict, WorkModel] = None):
        user_id = self._next_id
        children = children or []
        children = [
            child if isinstance(child, ChildModel) else ChildModel(**child)
            for child in children
        ]
        if not current_work:
            current_work = WorkModel(title='', address='')
        if isinstance(current_work, dict):
            current_work = WorkModel(**current_work)
        model = UserModel(
            id=user_id,
            created=pendulum.now(pendulum.UTC),
            first_name=first_name,
            last_name=last_name,
            age=age,
            sex=sex,
            children=children,
            current_work=current_work,
        )
        self._next_id += 1
        self.models[str(user_id)] = model
        return self.get_user_by_model(model)

    def get_user_by_name(self, first_name):
        for model in self.models.values():
            if model.first_name == first_name:
                return self.get_user_by_model(model)

    def delete_user(self, user_id: int):
        self._users_dict.pop(str(user_id))


def check_credentials(username, password, request):
    users: Users = request.root['users']
    user = users.get_user_by_name(username)
    if user:
        return [user.model.id]
