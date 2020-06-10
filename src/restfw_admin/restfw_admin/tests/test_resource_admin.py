# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 25.04.2020
"""
import colander
from restfw import schemas
from restfw.hal import HalResource, HalResourceWithEmbedded
from restfw.interfaces import MethodOptions
from restfw.schemas import GetEmbeddedSchema

from ..models import FieldModel, ValidatorModel
from ..resource_admin import Exclude, Only, ResourceAdmin, ViewSettings


class Child(schemas.MappingSchema):
    sex = schemas.StringNode(title='Sex', validator=colander.OneOf(['m', 'f']))
    name = schemas.StringNode(title='Name')
    age = schemas.UnsignedIntegerNode(title='Age', nullable=True)


class UserSchema(schemas.HalResourceSchema):
    id = schemas.UnsignedIntegerNode(title='ID')
    name = schemas.StringNode(title='User name')
    age = schemas.UnsignedIntegerNode(title='Age', nullable=True)
    sex = schemas.StringNode(title='Sex', validator=colander.OneOf(['m', 'f']))
    created = schemas.DateTimeNode(title='Created')
    children = schemas.SequenceNode(
        Child(title='Child'),
    )


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
    sex = schemas.StringNode(title='Sex', validator=colander.OneOf(['m', 'f']))
    children = schemas.SequenceNode(
        Child(title='Child', missing=colander.drop),
    )


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
        fields=Exclude({'children'})
    )


def test_get_list_view(pyramid_request):
    resource_admin = UsersAdmin(pyramid_request, 'items')
    view = resource_admin.get_list_view()
    fields = sorted(view.fields, key=lambda f: f.name)
    assert fields == [
        FieldModel(name='age', type='NumberField'),
        FieldModel(name='created', type='DateTimeField'),
        FieldModel(name='id', type='NumberField', label='ID'),
        FieldModel(name='name', type='TextField', label='User name'),
        FieldModel(
            name='sex', type='SelectField',
            props={
                'choices': [
                    {'id': 'm', 'name': 'M'},
                    {'id': 'f', 'name': 'F'},
                ]
            },
        ),
    ]

    # Exclude fields global
    resource_admin.fields = Exclude({'name', 'age'})
    view = resource_admin.get_list_view()
    fields = {f.name for f in view.fields}
    assert fields == {'id', 'created', 'sex'}

    # Exclude fields for view
    resource_admin.list_view.fields = Exclude({'sex'})
    view = resource_admin.get_list_view()
    fields = {f.name for f in view.fields}
    assert fields == {'id', 'created', 'children'}

    # Only fields for view
    resource_admin.list_view.fields = Only({'id'})
    view = resource_admin.get_list_view()
    fields = {f.name for f in view.fields}
    assert fields == {'id'}


def test_get_show_view(pyramid_request):
    resource_admin = UsersAdmin(pyramid_request, 'items')
    view = resource_admin.get_show_view()
    fields = sorted(view.fields, key=lambda f: f.name)
    assert fields == [
        FieldModel(name='age', type='NumberField'),
        FieldModel(
            name='children',
            type='ArrayField',
            props={
                'sub_fields': [
                    FieldModel(
                        name='sex',
                        type='SelectField',
                        label='Sex',
                        props={
                            'choices': [
                                {'id': 'm', 'name': 'M'},
                                {'id': 'f', 'name': 'F'},
                            ]
                        },
                    ),
                    FieldModel(
                        name='name',
                        type='TextField',
                        label='Name',
                    ),
                    FieldModel(
                        name='age',
                        type='NumberField',
                        label='Age',
                    ),
                ]
            },
        ),
        FieldModel(name='created', type='DateTimeField'),
        FieldModel(name='id', type='NumberField', label='ID'),
        FieldModel(name='name', type='TextField', label='User name'),
        FieldModel(
            name='sex', type='SelectField',
            props={
                'choices': [
                    {'id': 'm', 'name': 'M'},
                    {'id': 'f', 'name': 'F'},
                ]
            },
        ),
    ]

    # Exclude fields global
    resource_admin.fields = Exclude({'name', 'age'})
    view = resource_admin.get_show_view()
    fields = {f.name for f in view.fields}
    assert fields == {'id', 'created', 'sex', 'children'}

    # Exclude fields for view
    resource_admin.show_view.fields = Exclude({'sex'})
    view = resource_admin.get_show_view()
    fields = {f.name for f in view.fields}
    assert fields == {'id', 'created', 'children'}

    # Only fields for view
    resource_admin.show_view.fields = Only({'id'})
    view = resource_admin.get_show_view()
    fields = {f.name for f in view.fields}
    assert fields == {'id'}


def test_get_create_view(pyramid_request):
    resource_admin = UsersAdmin(pyramid_request, 'items')
    view = resource_admin.get_create_view()
    fields = sorted(view.fields, key=lambda f: f.name)

    assert fields == [
        FieldModel(
            type='NumberInput',
            name='age',
            validators=[
                ValidatorModel('min_value', 0),
                ValidatorModel('is_number')
            ]
        ),
        FieldModel(
            type='ArrayInput',
            name='children',
            validators=[ValidatorModel('required')],
            props={
                'sub_fields': [
                    FieldModel(
                        type='SelectInput',
                        name='sex',
                        validators=[ValidatorModel('required')],
                        props={
                            'choices': [
                                {'id': 'm', 'name': 'M'},
                                {'id': 'f', 'name': 'F'}
                            ]
                        }),
                    FieldModel(
                        type='TextInput',
                        name='name',
                        validators=[
                            ValidatorModel('required', ),
                            ValidatorModel('min_length', 1),
                        ]
                    ),
                    FieldModel(
                        type='NumberInput',
                        name='age',
                        validators=[
                            ValidatorModel('min_value', 0),
                            ValidatorModel('is_number'),
                        ],
                    )
                ]
            },
        ),
        FieldModel(
            type='TextInput',
            name='name',
            label='User name',
            validators=[
                ValidatorModel('required'),
                ValidatorModel('max_length', 50),
                ValidatorModel('regex', '^[a-zA-z0-9]+$'),
                ValidatorModel('min_length', 1)
            ],
        ),
        FieldModel(
            type='SelectInput',
            name='sex',
            validators=[ValidatorModel('required', )],
            props={
                'choices': [
                    {'id': 'm', 'name': 'M'},
                    {'id': 'f', 'name': 'F'},
                ]
            },
        )
    ]

    # Exclude fields global
    resource_admin.fields = Exclude({'age'})
    view = resource_admin.get_create_view()
    fields = {f.name for f in view.fields}
    assert fields == {'name', 'sex', 'children'}

    # Exclude fields for view
    resource_admin.create_view.fields = Exclude({'sex'})
    view = resource_admin.get_create_view()
    fields = {f.name for f in view.fields}
    assert fields == {'name', 'children'}

    # Only fields for view
    resource_admin.create_view.fields = Only({'sex'})
    view = resource_admin.get_create_view()
    fields = {f.name for f in view.fields}
    assert fields == {'sex'}


def test_get_edit_view(pyramid_request):
    resource_admin = UsersAdmin(pyramid_request, 'items')
    view = resource_admin.get_edit_view()
    fields = sorted(view.fields, key=lambda f: f.name)
    assert fields == [
        FieldModel(
            type='NumberInput',
            name='age',
            validators=[
                ValidatorModel('min_value', 0),
                ValidatorModel('is_number')
            ]
        ),
        FieldModel(
            type='ArrayInput',
            name='children',
            props={
                'sub_fields': [
                    FieldModel(
                        type='SelectInput',
                        name='sex',
                        validators=[ValidatorModel('required')],
                        props={
                            'choices': [
                                {'id': 'm', 'name': 'M'},
                                {'id': 'f', 'name': 'F'}
                            ]
                        }),
                    FieldModel(
                        type='TextInput',
                        name='name',
                        validators=[
                            ValidatorModel('required', ),
                            ValidatorModel('min_length', 1),
                        ]
                    ),
                    FieldModel(
                        type='NumberInput',
                        name='age',
                        validators=[
                            ValidatorModel('min_value', 0),
                            ValidatorModel('is_number'),
                        ],
                    )
                ]
            },
        ),
        FieldModel(
            type='TextInput',
            name='name',
            label='User name',
            validators=[
                ValidatorModel('max_length', 50),
                ValidatorModel('regex', '^[a-zA-z0-9]+$'),
                ValidatorModel('min_length', 1)
            ],
        ),
        FieldModel(
            type='SelectInput',
            name='sex',
            props={
                'choices': [
                    {'id': 'm', 'name': 'M'},
                    {'id': 'f', 'name': 'F'},
                ]
            },
        )
    ]

    # Exclude fields global
    resource_admin.fields = Exclude({'age'})
    view = resource_admin.get_edit_view()
    fields = {f.name for f in view.fields}
    assert fields == {'name', 'sex', 'children'}

    # Exclude fields for view
    resource_admin.edit_view.fields = Exclude({'sex'})
    view = resource_admin.get_edit_view()
    fields = {f.name for f in view.fields}
    assert fields == {'name', 'children'}

    # Only fields for view
    resource_admin.edit_view.fields = Only({'sex'})
    view = resource_admin.get_edit_view()
    fields = {f.name for f in view.fields}
    assert fields == {'sex'}
