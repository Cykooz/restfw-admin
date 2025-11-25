# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 25.04.2020
"""

import colander
import pytest
from cykooz.testing import D
from restfw import schemas, views
from restfw.hal import HalResource
from restfw.interfaces import MethodOptions

from .. import widgets, widgets as all_widgets
from ..models import FieldModel, ValidatorModel
from ..resource_admin import (
    Exclude,
    Only,
    ResourceAdmin,
    exclude_widgets,
    only_widgets,
    replace_widgets,
    unflat,
    ListViewSettings,
    Filters,
)
from ..resources import get_admin


# Users


class Child(schemas.MappingNode):
    sex = schemas.StringNode(title='Sex', validator=colander.OneOf(['m', 'f']))
    name = schemas.StringNode(title='Name')
    age = schemas.UnsignedIntegerNode(title='Age', nullable=True)
    toys = schemas.SequenceNode(
        schemas.StringNode(title='Toy name'),
        title='Toys',
    )
    birth_date = schemas.IntegerNode(
        title='Birth date',
        widget=(
            widgets.DateField(show_time=True),
            widgets.DateInput(),
        ),
    )


class Work(schemas.MappingNode):
    title = schemas.StringNode(
        title='Title', validator=schemas.LaconicNoneOf(['God', 'Duck'])
    )
    address = schemas.StringNode(title='Address')


def description_validator(node, value):
    if value == 'Bad Guy':
        raise colander.Invalid('Go to home, Bad Guy')


class UserSchema(schemas.HalResourceSchema):
    id = schemas.UnsignedIntegerNode(title='ID')
    name = schemas.StringNode(title='User name')
    age = schemas.UnsignedIntegerNode(title='Age', nullable=True)
    sex = schemas.StringNode(title='Sex', validator=colander.OneOf(['m', 'f']))
    description = schemas.EmptyStringNode(title='Description')
    created = schemas.DateTimeNode(title='Created')
    children = schemas.SequenceNode(
        Child(title='Child'),
    )
    current_work = Work(title='Current work')
    previews_work = Work(title='Previews work', nullable=True, missing=None)


class UsersSchema(schemas.HalResourceWithEmbeddedSchema):
    _embedded = schemas.EmbeddedNode(
        schemas.SequenceNode(
            UserSchema(title='User'), name='users', title='List of embedded users'
        ),
        missing=colander.drop,
    )


class GetUsersSchema(schemas.GetEmbeddedSchema):
    id = schemas.UnsignedIntegerNode(title='ID', missing=colander.drop)
    name = schemas.StringNode(title='User name', missing=colander.drop)
    sex = schemas.StringNode(
        title='Sex',
        validator=colander.OneOf(['m', 'f']),
        missing=colander.drop,
    )
    has_children = schemas.BooleanNode(
        title='Has children',
        missing=colander.drop,
    )


class CreateUserSchema(schemas.MappingNode):
    name = schemas.StringNode(
        title='User name',
        validator=colander.All(
            colander.Length(max=50),
            colander.Regex(r'^[a-zA-z0-9]+$'),
            colander.luhnok,
        ),
    )
    age = schemas.UnsignedIntegerNode(
        title='Age',
        nullable=True,
        missing=colander.drop,
    )
    sex = schemas.StringNode(
        title='Sex',
        validator=colander.OneOf(['m', 'f']),
        nullable=True,
        missing=None,
    )
    description = schemas.EmptyStringNode(
        title='Description', validator=description_validator, missing=''
    )
    children = schemas.SequenceNode(
        Child(title='Child', missing=colander.drop),
    )
    current_work = Work(title='Current work')
    previews_work = Work(title='Previews work', nullable=True, missing=None)


class PatchItemSchema(schemas.MappingNode):
    name = schemas.StringNode(
        title='User name',
        missing=colander.drop,
        validator=colander.All(
            colander.Length(max=50), colander.Regex(r'^[a-zA-z0-9]+$')
        ),
    )
    age = schemas.UnsignedIntegerNode(
        title='Age',
        nullable=True,
        missing=colander.drop,
    )
    sex = schemas.StringNode(
        title='Sex', missing=colander.drop, validator=colander.OneOf(['m', 'f'])
    )
    children = schemas.SequenceNode(
        Child(title='Child', missing=colander.drop),
        missing=colander.drop,
    )
    current_work = Work(title='Current work', missing=colander.drop)


class User(HalResource):
    pass


@views.resource_view_config(User)
class UserView(views.HalResourceView):
    options_for_get = MethodOptions(None, UserSchema, permission='users.get')
    options_for_patch = MethodOptions(
        PatchItemSchema, UserSchema, permission='users.edit'
    )


class Users(HalResource):
    pass


@views.resource_view_config(Users)
class UsersView(views.HalResourceWithEmbeddedView):
    options_for_get = MethodOptions(GetUsersSchema, UsersSchema, permission='users.get')
    options_for_post = MethodOptions(
        CreateUserSchema, UserSchema, permission='users.edit'
    )


class UsersAdmin(ResourceAdmin):
    title = 'Users'
    container_view_class = UsersView
    child_view_class = UserView
    location = '/users'
    index = 0
    list_view = ListViewSettings(
        fields=Only(
            'id',
            'created',
            'name',
            'age',
            'sex',
            'current_work.title',
            'previews_work.title',
        ),
        widgets={
            'current_work': {'title': widgets.TextField(label='Current work title')},
            'previews_work': {'title': widgets.TextField(label='Previews work title')},
        },
        filters=Filters(
            always_on=['id'],
        ),
    )


@pytest.fixture(autouse=True)
def scan(app_config):
    app_config.scan('restfw_admin.tests.test_resource_admin')
    app_config.commit()


@pytest.fixture(name='widgets')
def widgets_fixture():
    return {
        'name': all_widgets.TextField(),
        'child': all_widgets.ArrayField(
            fields={
                'name': all_widgets.TextField(),
                'sex': all_widgets.TextField(),
                'age': all_widgets.NumberField(),
            }
        ),
        'parent': all_widgets.ArrayField(
            fields={
                'name': all_widgets.TextField(),
                'age': all_widgets.NumberField(),
                'work': all_widgets.ArrayField(
                    fields={
                        'name': all_widgets.TextField(),
                        'phone': all_widgets.TextField(),
                    }
                ),
            }
        ),
        'phone': all_widgets.TextField(),
    }


def test_only_widgets(widgets):
    names = unflat(['child.age', 'child.name', 'parent.work.name', 'name'])
    res = only_widgets(widgets, names)
    assert res == {
        'child': all_widgets.ArrayField(
            fields={
                'age': all_widgets.NumberField(),
                'name': all_widgets.TextField(),
            }
        ),
        'parent': all_widgets.ArrayField(
            fields={
                'work': all_widgets.ArrayField(
                    fields={
                        'name': all_widgets.TextField(),
                    }
                ),
            }
        ),
        'name': all_widgets.TextField(),
    }
    assert list(res.keys()) == ['child', 'parent', 'name']


def test_exclude_widgets(widgets):
    names = unflat(
        ['child.sex', 'parent.work.phone', 'parent.name', 'parent.age', 'phone']
    )
    res = exclude_widgets(widgets, names)
    assert res == {
        'name': all_widgets.TextField(),
        'child': all_widgets.ArrayField(
            fields={
                'name': all_widgets.TextField(),
                'age': all_widgets.NumberField(),
            }
        ),
        'parent': all_widgets.ArrayField(
            fields={
                'work': all_widgets.ArrayField(
                    fields={
                        'name': all_widgets.TextField(),
                    }
                ),
            }
        ),
    }
    assert list(res.keys()) == ['name', 'child', 'parent']


def test_replace_widgets(widgets):
    replaces = {
        'name': all_widgets.TextField(label='New name'),
        'child': {
            'name': None,
            'age': all_widgets.TextField(),
            'not_a_field': all_widgets.TextField(),
        },
        'parent': {
            'work': {
                'name': all_widgets.SelectField(choices=[('w1', 'W1'), ('w2', 'W2')])
            }
        },
        'phone': None,
    }
    replace_widgets(widgets, replaces)
    assert widgets == {
        'name': all_widgets.TextField(label='New name'),
        'child': all_widgets.ArrayField(
            fields={
                'sex': all_widgets.TextField(),
                'age': all_widgets.TextField(),
            }
        ),
        'parent': all_widgets.ArrayField(
            fields={
                'name': all_widgets.TextField(),
                'age': all_widgets.NumberField(),
                'work': all_widgets.ArrayField(
                    fields={
                        'name': all_widgets.SelectField(
                            choices=[('w1', 'W1'), ('w2', 'W2')]
                        ),
                        'phone': all_widgets.TextField(),
                    }
                ),
            }
        ),
    }


def test_get_user_list_view(pyramid_request):
    resource_admin = UsersAdmin(pyramid_request, 'items')
    view = resource_admin.get_list_view()
    fields = sorted(view.fields, key=lambda f: f.source)
    assert fields == [
        FieldModel(
            type='NumberField',
            source='age',
            params={
                'label': 'Age',
                'options': {
                    'useGrouping': False,
                },
            },
        ),
        FieldModel(
            type='DateField',
            source='created',
            params={'label': 'Created', 'showTime': True},
        ),
        FieldModel(
            type='TextField',
            source='current_work.title',
            params={'label': 'Current work title'},
        ),
        FieldModel(
            type='NumberField',
            source='id',
            params={
                'label': 'ID',
                'options': {
                    'useGrouping': False,
                },
            },
        ),
        FieldModel(type='TextField', source='name', params={'label': 'User name'}),
        FieldModel(
            type='TextField',
            source='previews_work.title',
            params={'label': 'Previews work title'},
        ),
        FieldModel(
            type='SelectField',
            source='sex',
            params={
                'label': 'Sex',
                'choices': [
                    {'id': 'm', 'name': 'M'},
                    {'id': 'f', 'name': 'F'},
                ],
            },
        ),
    ]
    filters = sorted(view.filters, key=lambda f: f.source)
    assert filters == [
        FieldModel(
            type='BooleanInput',
            source='has_children',
            params={'label': 'Has children'},
        ),
        FieldModel(
            type='TextInput',
            source='id',
            params={'label': 'ID', 'alwaysOn': True},
            validators=[
                ValidatorModel(name='minValue', args=(0,)),
                ValidatorModel(name='number'),
            ],
        ),
        FieldModel(
            type='TextInput',
            source='name',
            params={'label': 'User name'},
            validators=[
                ValidatorModel(name='minLength', args=(1,)),
            ],
        ),
        FieldModel(
            type='SelectInput',
            source='sex',
            params={
                'label': 'Sex',
                'choices': [
                    {'id': 'm', 'name': 'M'},
                    {'id': 'f', 'name': 'F'},
                ],
            },
        ),
    ]

    # Exclude fields global
    resource_admin.fields = Exclude('name', 'age')
    view = resource_admin.get_list_view()
    fields = {f.source for f in view.fields}
    assert fields == {
        'id',
        'created',
        'sex',
        'current_work.title',
        'previews_work.title',
    }
    filters = sorted(view.filters, key=lambda f: f.source)
    assert filters == [
        FieldModel(
            type='BooleanInput',
            source='has_children',
            params={'label': 'Has children'},
        ),
        FieldModel(
            type='TextInput',
            source='id',
            params={'label': 'ID', 'alwaysOn': True},
            validators=[
                ValidatorModel(name='minValue', args=(0,)),
                ValidatorModel(name='number'),
            ],
        ),
        # Filter by name is not excluded by global settings
        FieldModel(
            type='TextInput',
            source='name',
            params={'label': 'User name'},
            validators=[
                ValidatorModel(name='minLength', args=(1,)),
            ],
        ),
        FieldModel(
            type='SelectInput',
            source='sex',
            params={
                'label': 'Sex',
                'choices': [
                    {'id': 'm', 'name': 'M'},
                    {'id': 'f', 'name': 'F'},
                ],
            },
        ),
    ]

    # Exclude fields for view
    resource_admin.list_view.fields = Exclude('sex')
    view = resource_admin.get_list_view()
    fields = {f.source for f in view.fields}
    assert fields == {
        'created',
        'current_work',
        'description',
        'children',
        'previews_work',
        'id',
    }

    # Only fields for view
    resource_admin.list_view.fields = Only('id')
    view = resource_admin.get_list_view()
    fields = {f.source for f in view.fields}
    assert fields == {'id'}


def test_get_user_show_view(pyramid_request):
    resource_admin = UsersAdmin(pyramid_request, 'items')
    view = resource_admin.get_show_view()
    fields = sorted(view.fields, key=lambda f: f.source)
    assert fields == [
        FieldModel(
            type='NumberField',
            source='age',
            params={
                'label': 'Age',
                'options': {
                    'useGrouping': False,
                },
            },
        ),
        FieldModel(
            type='ArrayField',
            source='children',
            params={
                'label': 'Children',
                'fields': [
                    FieldModel(
                        type='SelectField',
                        source='sex',
                        params={
                            'label': 'Sex',
                            'choices': [
                                {'id': 'm', 'name': 'M'},
                                {'id': 'f', 'name': 'F'},
                            ],
                        },
                    ),
                    FieldModel(
                        type='TextField', source='name', params={'label': 'Name'}
                    ),
                    FieldModel(
                        type='NumberField',
                        source='age',
                        params={
                            'label': 'Age',
                            'options': {
                                'useGrouping': False,
                            },
                        },
                    ),
                    FieldModel(
                        type='NestedArrayField',
                        source='toys',
                        params={
                            'label': 'Toys',
                            'fields': None,
                            'single_field': FieldModel(
                                type='TextField',
                                source='_value',
                                params={
                                    'label': 'Toy name',
                                },
                            ),
                        },
                    ),
                    FieldModel(
                        type='DateField',
                        source='birth_date',
                        params={
                            'label': 'Birth date',
                            'showTime': True,
                        },
                    ),
                ],
            },
        ),
        FieldModel(
            type='DateField',
            source='created',
            params={'label': 'Created', 'showTime': True},
        ),
        FieldModel(
            type='MappingField',
            source='current_work',
            params={
                'label': 'Current work',
                'fields': [
                    FieldModel(
                        type='TextField',
                        source='title',
                        params={'label': 'Title'},
                    ),
                    FieldModel(
                        type='TextField',
                        source='address',
                        params={'label': 'Address'},
                    ),
                ],
            },
        ),
        FieldModel(
            type='TextField', source='description', params={'label': 'Description'}
        ),
        FieldModel(
            type='NumberField',
            source='id',
            params={
                'label': 'ID',
                'options': {
                    'useGrouping': False,
                },
            },
        ),
        FieldModel(type='TextField', source='name', params={'label': 'User name'}),
        FieldModel(
            type='MappingField',
            source='previews_work',
            params={
                'label': 'Previews work',
                'fields': [
                    FieldModel(
                        type='TextField',
                        source='title',
                        params={'label': 'Title'},
                    ),
                    FieldModel(
                        type='TextField',
                        source='address',
                        params={'label': 'Address'},
                    ),
                ],
            },
        ),
        FieldModel(
            type='SelectField',
            source='sex',
            params={
                'label': 'Sex',
                'choices': [{'id': 'm', 'name': 'M'}, {'id': 'f', 'name': 'F'}],
            },
        ),
    ]

    # Exclude fields global
    resource_admin.fields = Exclude('name', 'age')
    view = resource_admin.get_show_view()
    fields = {f.source for f in view.fields}
    assert fields == {
        'id',
        'created',
        'sex',
        'description',
        'children',
        'current_work',
        'previews_work',
    }

    # Exclude fields for view
    resource_admin.show_view.fields = Exclude('sex')
    view = resource_admin.get_show_view()
    fields = {f.source for f in view.fields}
    assert fields == {
        'id',
        'created',
        'children',
        'description',
        'current_work',
        'previews_work',
    }

    # Only fields for view
    resource_admin.show_view.fields = Only('id')
    view = resource_admin.get_show_view()
    fields = {f.source for f in view.fields}
    assert fields == {'id'}


def test_get_user_create_view(pyramid_request):
    resource_admin = UsersAdmin(pyramid_request, 'items')
    view = resource_admin.get_create_view()
    fields = sorted(view.fields, key=lambda f: f.source)

    assert fields == [
        FieldModel(
            type='TextInput',
            source='age',
            params={'label': 'Age'},
            validators=[
                ValidatorModel(name='minValue', args=(0,)),
                ValidatorModel(name='number'),
            ],
        ),
        FieldModel(
            type='ArrayInput',
            source='children',
            params={
                'label': 'Children',
                'fields': [
                    FieldModel(
                        type='SelectInput',
                        source='sex',
                        params={
                            'label': 'Sex',
                            'choices': [
                                {'id': 'm', 'name': 'M'},
                                {'id': 'f', 'name': 'F'},
                            ],
                        },
                        validators=[ValidatorModel(name='required', args=())],
                    ),
                    FieldModel(
                        type='TextInput',
                        source='name',
                        params={'label': 'Name'},
                        validators=[
                            ValidatorModel(name='required', args=()),
                            ValidatorModel(name='minLength', args=(1,)),
                        ],
                    ),
                    FieldModel(
                        type='TextInput',
                        source='age',
                        params={'label': 'Age'},
                        validators=[
                            ValidatorModel(name='minValue', args=(0,)),
                            ValidatorModel(name='number'),
                        ],
                    ),
                    FieldModel(
                        type='ArrayInput',
                        source='toys',
                        params={
                            'label': 'Toys',
                            'fields': [
                                FieldModel(
                                    type='TextInput',
                                    source='',
                                    params={'label': 'Toy name'},
                                    validators=[
                                        ValidatorModel(name='required', args=()),
                                        ValidatorModel(name='minLength', args=(1,)),
                                    ],
                                )
                            ],
                        },
                        validators=[ValidatorModel(name='required', args=())],
                    ),
                    FieldModel(
                        type='DateInput',
                        source='birth_date',
                        params={
                            'label': 'Birth date',
                        },
                    ),
                ],
            },
            validators=[ValidatorModel(name='required', args=())],
        ),
        FieldModel(
            type='MappingInput',
            source='current_work',
            params={
                'label': 'Current work',
                'fields': [
                    FieldModel(
                        type='TextInput',
                        source='title',
                        params={'label': 'Title'},
                        validators=[
                            ValidatorModel(name='required', args=()),
                            ValidatorModel(name='minLength', args=(1,)),
                        ],
                    ),
                    FieldModel(
                        type='TextInput',
                        source='address',
                        params={'label': 'Address'},
                        validators=[
                            ValidatorModel(name='required', args=()),
                            ValidatorModel(name='minLength', args=(1,)),
                        ],
                    ),
                ],
            },
        ),
        FieldModel(
            type='TextInput',
            source='description',
            params={
                'label': 'Description',
                'defaultValue': '',
            },
            validators=[],
        ),
        FieldModel(
            type='TextInput',
            source='name',
            params={'label': 'User name'},
            validators=[
                ValidatorModel(name='required', args=()),
                ValidatorModel(name='maxLength', args=(50,)),
                ValidatorModel(name='regex', args=('^[a-zA-z0-9]+$',)),
                ValidatorModel(name='minLength', args=(1,)),
            ],
        ),
        FieldModel(
            type='MappingInput',
            source='previews_work',
            params={
                'label': 'Previews work',
                'fields': [
                    FieldModel(
                        type='TextInput',
                        source='title',
                        params={'label': 'Title'},
                        validators=[
                            ValidatorModel(name='required', args=()),
                            ValidatorModel(name='minLength', args=(1,)),
                        ],
                    ),
                    FieldModel(
                        type='TextInput',
                        source='address',
                        params={'label': 'Address'},
                        validators=[
                            ValidatorModel(name='required', args=()),
                            ValidatorModel(name='minLength', args=(1,)),
                        ],
                    ),
                ],
            },
        ),
        FieldModel(
            type='SelectInput',
            source='sex',
            params={
                'label': 'Sex',
                'choices': [{'id': 'm', 'name': 'M'}, {'id': 'f', 'name': 'F'}],
                'emptyText': '<none>',
                'emptyValue': None,
            },
            validators=[],
        ),
    ]

    # Exclude fields global
    resource_admin.fields = Exclude('age')
    view = resource_admin.get_create_view()
    fields = {f.source for f in view.fields}
    assert fields == {
        'name',
        'sex',
        'description',
        'children',
        'current_work',
        'previews_work',
    }

    # Exclude fields for view
    resource_admin.create_view.fields = Exclude('sex')
    view = resource_admin.get_create_view()
    fields = {f.source for f in view.fields}
    assert fields == {
        'name',
        'children',
        'description',
        'current_work',
        'previews_work',
    }

    # Only fields for view
    resource_admin.create_view.fields = Only('sex')
    view = resource_admin.get_create_view()
    fields = {f.source for f in view.fields}
    assert fields == {'sex'}


def test_get_user_edit_view(pyramid_request):
    resource_admin = UsersAdmin(pyramid_request, 'items')
    view = resource_admin.get_edit_view()
    fields = sorted(view.fields, key=lambda f: f.source)
    assert fields == [
        FieldModel(
            type='TextInput',
            source='age',
            params={'label': 'Age'},
            validators=[
                ValidatorModel(name='minValue', args=(0,)),
                ValidatorModel(name='number'),
            ],
        ),
        FieldModel(
            type='ArrayInput',
            source='children',
            params={
                'label': 'Children',
                'fields': [
                    FieldModel(
                        type='SelectInput',
                        source='sex',
                        params={
                            'label': 'Sex',
                            'choices': [
                                {'id': 'm', 'name': 'M'},
                                {'id': 'f', 'name': 'F'},
                            ],
                        },
                        validators=[ValidatorModel(name='required', args=())],
                    ),
                    FieldModel(
                        type='TextInput',
                        source='name',
                        params={'label': 'Name'},
                        validators=[
                            ValidatorModel(name='required', args=()),
                            ValidatorModel(name='minLength', args=(1,)),
                        ],
                    ),
                    FieldModel(
                        type='TextInput',
                        source='age',
                        params={'label': 'Age'},
                        validators=[
                            ValidatorModel(name='minValue', args=(0,)),
                            ValidatorModel(name='number'),
                        ],
                    ),
                    FieldModel(
                        type='ArrayInput',
                        source='toys',
                        params={
                            'label': 'Toys',
                            'fields': [
                                FieldModel(
                                    type='TextInput',
                                    source='',
                                    params={'label': 'Toy name'},
                                    validators=[
                                        ValidatorModel(name='required', args=()),
                                        ValidatorModel(name='minLength', args=(1,)),
                                    ],
                                )
                            ],
                        },
                        validators=[ValidatorModel(name='required', args=())],
                    ),
                    FieldModel(
                        type='DateInput',
                        source='birth_date',
                        params={
                            'label': 'Birth date',
                        },
                    ),
                ],
            },
        ),
        FieldModel(
            type='MappingInput',
            source='current_work',
            params={
                'label': 'Current work',
                'fields': [
                    FieldModel(
                        type='TextInput',
                        source='title',
                        params={'label': 'Title'},
                        validators=[
                            ValidatorModel(name='required', args=()),
                            ValidatorModel(name='minLength', args=(1,)),
                        ],
                    ),
                    FieldModel(
                        type='TextInput',
                        source='address',
                        params={'label': 'Address'},
                        validators=[
                            ValidatorModel(name='required', args=()),
                            ValidatorModel(name='minLength', args=(1,)),
                        ],
                    ),
                ],
            },
        ),
        FieldModel(
            type='TextInput',
            source='name',
            params={'label': 'User name'},
            validators=[
                ValidatorModel(name='maxLength', args=(50,)),
                ValidatorModel(name='regex', args=('^[a-zA-z0-9]+$',)),
                ValidatorModel(name='minLength', args=(1,)),
            ],
        ),
        FieldModel(
            type='SelectInput',
            source='sex',
            params={
                'label': 'Sex',
                'choices': [{'id': 'm', 'name': 'M'}, {'id': 'f', 'name': 'F'}],
            },
        ),
    ]

    # Exclude fields global
    resource_admin.fields = Exclude('age')
    view = resource_admin.get_edit_view()
    fields = {f.source for f in view.fields}
    assert fields == {'name', 'sex', 'children', 'current_work'}

    # Exclude fields for view
    resource_admin.edit_view.fields = Exclude('sex')
    view = resource_admin.get_edit_view()
    fields = {f.source for f in view.fields}
    assert fields == {'name', 'children', 'current_work'}

    # Only fields for view
    resource_admin.edit_view.fields = Only('sex')
    view = resource_admin.get_edit_view()
    fields = {f.source for f in view.fields}
    assert fields == {'sex'}


def test_api_info(web_app, pyramid_request, app_config):
    app_config.add_resource_admin(UsersAdmin, name='users')
    app_config.commit()

    api_info = get_admin(pyramid_request.root)['api_info.json']
    url = pyramid_request.resource_url(api_info)
    res = web_app.get(url)
    assert res.json == {
        '_links': {'self': {'href': url}},
        'title': 'Admin UI',
        'root_url': 'http://localhost',
        'resources': D(),
        'extra': {},
    }
