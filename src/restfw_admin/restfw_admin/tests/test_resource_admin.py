# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 25.04.2020
"""
import colander
import pytest
from restfw import schemas
from restfw.hal import HalResource, HalResourceWithEmbedded
from restfw.interfaces import MethodOptions
from restfw.schemas import GetEmbeddedSchema

from .. import widgets as all_widgets
from ..models import FieldModel, ValidatorModel
from ..resource_admin import (
    Exclude, Only, ResourceAdmin, ViewSettings, exclude_widgets, only_widgets, replace_widgets,
    unflat
)


# Users

class Child(schemas.MappingSchema):
    sex = schemas.StringNode(title='Sex', validator=colander.OneOf(['m', 'f']))
    name = schemas.StringNode(title='Name')
    age = schemas.UnsignedIntegerNode(title='Age', nullable=True)
    toys = schemas.SequenceNode(
        schemas.StringNode(title='Toy name'),
        title='Toys',
    )


class Work(schemas.MappingSchema):
    title = schemas.StringNode(title='Title', validator=schemas.LaconicNoneOf(['God', 'Duck']))
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


class UsersSchema(schemas.HalResourceWithEmbeddedSchema):
    _embedded = schemas.EmbeddedNode(
        schemas.SequenceNode(
            UserSchema(title='User'),
            name='users', title='List of embedded users'
        ),
        missing=colander.drop,
    )


class CreateUserSchema(schemas.MappingSchema):
    name = schemas.StringNode(
        title='User name',
        validator=colander.All(
            colander.Length(max=50),
            colander.Regex(r'^[a-zA-z0-9]+$'),
            colander.luhnok,
        ),
    )
    age = schemas.UnsignedIntegerNode(
        title='Age', nullable=True, missing=colander.drop,
    )
    sex = schemas.StringNode(title='Sex', validator=colander.OneOf(['m', 'f']), nullable=True)
    description = schemas.EmptyStringNode(title='Description', validator=description_validator)
    children = schemas.SequenceNode(
        Child(title='Child', missing=colander.drop),
    )
    current_work = Work(title='Current work')


class PatchItemSchema(schemas.MappingSchema):
    name = schemas.StringNode(
        title='User name', missing=colander.drop,
        validator=colander.All(
            colander.Length(max=50),
            colander.Regex(r'^[a-zA-z0-9]+$')
        ),
    )
    age = schemas.UnsignedIntegerNode(
        title='Age', nullable=True, missing=colander.drop,
    )
    sex = schemas.StringNode(
        title='Sex', missing=colander.drop,
        validator=colander.OneOf(['m', 'f'])
    )
    children = schemas.SequenceNode(
        Child(title='Child', missing=colander.drop),
        missing=colander.drop,
    )
    current_work = Work(title='Current work', missing=colander.drop)


class User(HalResource):
    options_for_get = MethodOptions(None, UserSchema, permission='users.get')
    options_for_patch = MethodOptions(PatchItemSchema, UserSchema, permission='users.edit')


class Users(HalResourceWithEmbedded):
    options_for_get = MethodOptions(GetEmbeddedSchema, UsersSchema, permission='users.get')
    options_for_post = MethodOptions(CreateUserSchema, UserSchema, permission='users.edit')


class UsersAdmin(ResourceAdmin):
    container = Users
    child = User
    title = 'Users'
    location = '/users'
    index = 0
    list_view = ViewSettings(
        fields=Exclude('children', 'current_work')
    )


@pytest.fixture(name='widgets')
def widgets_fixture():
    return {
        'name': all_widgets.TextField(),
        'child': all_widgets.ArrayField(fields={
            'name': all_widgets.TextField(),
            'sex': all_widgets.TextField(),
            'age': all_widgets.NumberField(),
        }),
        'parent': all_widgets.ArrayField(fields={
            'name': all_widgets.TextField(),
            'age': all_widgets.NumberField(),
            'work': all_widgets.ArrayField(fields={
                'name': all_widgets.TextField(),
                'phone': all_widgets.TextField(),
            }),
        }),
        'phone': all_widgets.TextField(),
    }


def test_only_widgets(widgets):
    names = unflat(['child.age', 'child.name', 'parent.work.name', 'name'])
    res = only_widgets(widgets, names)
    assert res == {
        'child': all_widgets.ArrayField(fields={
            'age': all_widgets.NumberField(),
            'name': all_widgets.TextField(),
        }),
        'parent': all_widgets.ArrayField(fields={
            'work': all_widgets.ArrayField(fields={
                'name': all_widgets.TextField(),
            }),
        }),
        'name': all_widgets.TextField(),
    }
    assert list(res.keys()) == ['child', 'parent', 'name']


def test_exclude_widgets(widgets):
    names = unflat(['child.sex', 'parent.work.phone', 'parent.name', 'parent.age', 'phone'])
    res = exclude_widgets(widgets, names)
    assert res == {
        'name': all_widgets.TextField(),
        'child': all_widgets.ArrayField(fields={
            'name': all_widgets.TextField(),
            'age': all_widgets.NumberField(),
        }),
        'parent': all_widgets.ArrayField(fields={
            'work': all_widgets.ArrayField(fields={
                'name': all_widgets.TextField(),
            }),
        }),
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
        'child': all_widgets.ArrayField(fields={
            'sex': all_widgets.TextField(),
            'age': all_widgets.TextField(),
        }),
        'parent': all_widgets.ArrayField(fields={
            'name': all_widgets.TextField(),
            'age': all_widgets.NumberField(),
            'work': all_widgets.ArrayField(fields={
                'name': all_widgets.SelectField(choices=[('w1', 'W1'), ('w2', 'W2')]),
                'phone': all_widgets.TextField(),
            }),
        }),
    }


def test_get_user_list_view(pyramid_request):
    resource_admin = UsersAdmin(pyramid_request, 'items')
    view = resource_admin.get_list_view()
    fields = sorted(view.fields, key=lambda f: f.source)
    assert fields == [
        FieldModel(type='NumberField', source='age', params={'label': 'Age'}),
        FieldModel(type='DateField', source='created', params={'label': 'Created', 'showTime': True}),
        FieldModel(type='TextField', source='description', params={'label': 'Description'}),
        FieldModel(type='NumberField', source='id', params={'label': 'ID'}),
        FieldModel(type='TextField', source='name', params={'label': 'User name'}),
        FieldModel(
            type='SelectField', source='sex',
            params={
                'label': 'Sex',
                'choices': [
                    {'id': 'm', 'name': 'M'},
                    {'id': 'f', 'name': 'F'},
                ]
            },
        ),
    ]

    # Exclude fields global
    resource_admin.fields = Exclude('name', 'age')
    view = resource_admin.get_list_view()
    fields = {f.source for f in view.fields}
    assert fields == {'id', 'created', 'sex', 'description'}

    # Exclude fields for view
    resource_admin.list_view.fields = Exclude('sex')
    view = resource_admin.get_list_view()
    fields = {f.source for f in view.fields}
    assert fields == {'id', 'created', 'children', 'description', 'current_work'}

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
        FieldModel(type='NumberField', source='age', params={'label': 'Age'}),
        FieldModel(
            type='ArrayField',
            source='children',
            params={
                'label': 'Children',
                'fields': [
                    FieldModel(
                        type='SelectField', source='sex',
                        params={
                            'label': 'Sex',
                            'choices': [{'id': 'm', 'name': 'M'}, {'id': 'f', 'name': 'F'}]
                        }
                    ),
                    FieldModel(type='TextField', source='name', params={'label': 'Name'}),
                    FieldModel(type='NumberField', source='age', params={'label': 'Age'}),
                    FieldModel(
                        type='ArrayField',
                        source='toys',
                        params={
                            'label': 'Toys',
                            'fields': [
                                FieldModel(type='TextField', source='', params={'label': 'Toy name'}),
                            ]
                        },
                    ),
                ]
            }),
        FieldModel(type='DateField', source='created', params={'label': 'Created', 'showTime': True}),
        FieldModel(
            type='MappingField',
            source='current_work',
            params={
                'label': 'Current work',
                'fields': [
                    FieldModel(
                        type='TextField', source='title', params={'label': 'Title'},
                    ),
                    FieldModel(
                        type='TextField', source='address', params={'label': 'Address'},
                    )
                ]
            },
        ),
        FieldModel(type='TextField', source='description', params={'label': 'Description'}),
        FieldModel(type='NumberField', source='id', params={'label': 'ID'}),
        FieldModel(type='TextField', source='name', params={'label': 'User name'}),
        FieldModel(
            type='SelectField', source='sex',
            params={
                'label': 'Sex',
                'choices': [{'id': 'm', 'name': 'M'}, {'id': 'f', 'name': 'F'}]
            }
        ),
    ]

    # Exclude fields global
    resource_admin.fields = Exclude('name', 'age')
    view = resource_admin.get_show_view()
    fields = {f.source for f in view.fields}
    assert fields == {'id', 'created', 'sex', 'description', 'children', 'current_work'}

    # Exclude fields for view
    resource_admin.show_view.fields = Exclude('sex')
    view = resource_admin.get_show_view()
    fields = {f.source for f in view.fields}
    assert fields == {'id', 'created', 'children', 'description', 'current_work'}

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
            type='TextInput', source='age',
            params={'label': 'Age'},
            validators=[
                ValidatorModel(name='minValue', args=(0,)),
                ValidatorModel(name='number'),
            ]
        ),
        FieldModel(
            type='ArrayInput', source='children',
            params={
                'label': 'Children',
                'fields': [
                    FieldModel(
                        type='SelectInput', source='sex',
                        params={
                            'label': 'Sex',
                            'choices': [{'id': 'm', 'name': 'M'}, {'id': 'f', 'name': 'F'}]
                        },
                        validators=[ValidatorModel(name='required', args=())]
                    ),
                    FieldModel(
                        type='TextInput', source='name',
                        params={'label': 'Name'},
                        validators=[ValidatorModel(name='required', args=()),
                                    ValidatorModel(name='minLength', args=(1,))]
                    ),
                    FieldModel(
                        type='TextInput', source='age',
                        params={'label': 'Age'},
                        validators=[
                            ValidatorModel(name='minValue', args=(0,)),
                            ValidatorModel(name='number'),
                        ]
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
                                    ]
                                )
                            ]
                        },
                        validators=[ValidatorModel(name='required', args=())]
                    ),
                ]
            },
            validators=[ValidatorModel(name='required', args=())]
        ),
        FieldModel(
            type='MappingInput',
            source='current_work',
            params={
                'label': 'Current work',
                'fields': [
                    FieldModel(
                        type='TextInput', source='title', params={'label': 'Title'},
                        validators=[
                            ValidatorModel(name='required', args=()),
                            ValidatorModel(name='minLength', args=(1,))
                        ]
                    ),
                    FieldModel(
                        type='TextInput', source='address', params={'label': 'Address'},
                        validators=[
                            ValidatorModel(name='required', args=()),
                            ValidatorModel(name='minLength', args=(1,))
                        ]
                    )
                ]
            },
        ),
        FieldModel(
            type='TextInput',
            source='description',
            params={'label': 'Description'},
            validators=[ValidatorModel(name='required')]
        ),
        FieldModel(
            type='TextInput', source='name',
            params={'label': 'User name'},
            validators=[
                ValidatorModel(name='required', args=()), ValidatorModel(name='maxLength', args=(50,)),
                ValidatorModel(name='regex', args=('^[a-zA-z0-9]+$',)),
                ValidatorModel(name='minLength', args=(1,))
            ]
        ),
        FieldModel(
            type='SelectInput', source='sex',
            params={
                'label': 'Sex',
                'choices': [{'id': 'm', 'name': 'M'}, {'id': 'f', 'name': 'F'}],
                'allowEmpty': True,
                'emptyText': '<none>',
                'emptyValue': None,
            },
            validators=[ValidatorModel(name='required', args=())]
        ),
    ]

    # Exclude fields global
    resource_admin.fields = Exclude('age')
    view = resource_admin.get_create_view()
    fields = {f.source for f in view.fields}
    assert fields == {'name', 'sex', 'description', 'children', 'current_work'}

    # Exclude fields for view
    resource_admin.create_view.fields = Exclude('sex')
    view = resource_admin.get_create_view()
    fields = {f.source for f in view.fields}
    assert fields == {'name', 'children', 'description', 'current_work'}

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
            type='TextInput', source='age',
            params={'label': 'Age'},
            validators=[
                ValidatorModel(name='minValue', args=(0,)),
                ValidatorModel(name='number'),
            ]
        ),
        FieldModel(
            type='ArrayInput', source='children',
            params={
                'label': 'Children',
                'fields': [
                    FieldModel(
                        type='SelectInput', source='sex',
                        params={
                            'label': 'Sex',
                            'choices': [{'id': 'm', 'name': 'M'}, {'id': 'f', 'name': 'F'}]
                        },
                        validators=[ValidatorModel(name='required', args=())]
                    ),
                    FieldModel(
                        type='TextInput', source='name', params={'label': 'Name'},
                        validators=[ValidatorModel(name='required', args=()),
                                    ValidatorModel(name='minLength', args=(1,))]
                    ),
                    FieldModel(
                        type='TextInput', source='age',
                        params={'label': 'Age'},
                        validators=[
                            ValidatorModel(name='minValue', args=(0,)),
                            ValidatorModel(name='number'),
                        ]
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
                                    ]
                                )
                            ]
                        },
                        validators=[ValidatorModel(name='required', args=())]
                    ),
                ]
            },
        ),
        FieldModel(
            type='MappingInput',
            source='current_work',
            params={
                'label': 'Current work',
                'fields': [
                    FieldModel(
                        type='TextInput', source='title', params={'label': 'Title'},
                        validators=[
                            ValidatorModel(name='required', args=()),
                            ValidatorModel(name='minLength', args=(1,))
                        ]
                    ),
                    FieldModel(
                        type='TextInput', source='address', params={'label': 'Address'},
                        validators=[
                            ValidatorModel(name='required', args=()),
                            ValidatorModel(name='minLength', args=(1,))
                        ]
                    )
                ]
            },
        ),
        FieldModel(
            type='TextInput', source='name',
            params={'label': 'User name'},
            validators=[
                ValidatorModel(name='maxLength', args=(50,)),
                ValidatorModel(name='regex', args=('^[a-zA-z0-9]+$',)),
                ValidatorModel(name='minLength', args=(1,))
            ]
        ),
        FieldModel(
            type='SelectInput', source='sex',
            params={
                'label': 'Sex',
                'choices': [{'id': 'm', 'name': 'M'}, {'id': 'f', 'name': 'F'}]
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
