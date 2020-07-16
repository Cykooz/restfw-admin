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
from ..resource_admin import Exclude, Only, ResourceAdmin, ViewSettings, exclude_widgets, only_widgets, unflat


# Users

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
        fields=Exclude('children')
    )


# Docs

class DocSchema(schemas.HalResourceSchema):
    id = schemas.UnsignedIntegerNode(title='ID')
    user_id = schemas.IntegerNode(title='User ID')
    data = schemas.EmptyStringNode(title='Document data')


class DocsSchema(schemas.HalResourceWithEmbeddedSchema):
    _embedded = schemas.EmbeddedNode(
        schemas.SequenceNode(
            DocSchema(title='Document'),
            name='docs', title='List of embedded documents'
        ),
        missing=colander.drop,
    )


class CreateDocSchema(schemas.MappingSchema):
    user_id = schemas.IntegerNode(title='User ID')
    data = schemas.EmptyStringNode(title='Document data')


class Doc(HalResource):
    options_for_get = MethodOptions(None, DocSchema, permission='docs.get')
    options_for_delete = MethodOptions(None, None, permission='docs.edit')


class Docs(HalResourceWithEmbedded):
    options_for_get = MethodOptions(GetEmbeddedSchema, DocsSchema, permission='docs.get')
    options_for_post = MethodOptions(CreateDocSchema, DocSchema, permission='docs.edit')


class DocsAdmin(ResourceAdmin):
    container = Docs
    child = Doc
    title = 'Documents'
    location = '/docs'
    index = 1
    list_view = ViewSettings(
        fields=Exclude('data')
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
            'age': all_widgets.TextField(),
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


def test_get_user_list_view(pyramid_request):
    resource_admin = UsersAdmin(pyramid_request, 'items')
    view = resource_admin.get_list_view()
    fields = sorted(view.fields, key=lambda f: f.source)
    assert fields == [
        FieldModel(type='NumberField', source='age', params={'label': 'Age'}),
        FieldModel(type='DateField', source='created', params={'label': 'Created', 'showTime': True}),
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
    assert fields == {'id', 'created', 'sex'}

    # Exclude fields for view
    resource_admin.list_view.fields = Exclude('sex')
    view = resource_admin.get_list_view()
    fields = {f.source for f in view.fields}
    assert fields == {'id', 'created', 'children'}

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
                    FieldModel(type='NumberField', source='age', params={'label': 'Age'})
                ]
            }),
        FieldModel(type='DateField', source='created', params={'label': 'Created', 'showTime': True}),
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
    assert fields == {'id', 'created', 'sex', 'children'}

    # Exclude fields for view
    resource_admin.show_view.fields = Exclude('sex')
    view = resource_admin.get_show_view()
    fields = {f.source for f in view.fields}
    assert fields == {'id', 'created', 'children'}

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
            type='NumberInput', source='age',
            params={'label': 'Age', 'min': 0},
            validators=[ValidatorModel(name='minValue', args=(0,))]
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
                        type='NumberInput', source='age',
                        params={'label': 'Age', 'min': 0},
                        validators=[ValidatorModel(name='minValue', args=(0,))]
                    )
                ]
            },
            validators=[ValidatorModel(name='required', args=())]
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
                'choices': [{'id': 'm', 'name': 'M'}, {'id': 'f', 'name': 'F'}]
            },
            validators=[ValidatorModel(name='required', args=())]
        ),
    ]

    # Exclude fields global
    resource_admin.fields = Exclude('age')
    view = resource_admin.get_create_view()
    fields = {f.source for f in view.fields}
    assert fields == {'name', 'sex', 'children'}

    # Exclude fields for view
    resource_admin.create_view.fields = Exclude('sex')
    view = resource_admin.get_create_view()
    fields = {f.source for f in view.fields}
    assert fields == {'name', 'children'}

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
            type='NumberInput', source='age',
            params={'label': 'Age', 'min': 0},
            validators=[ValidatorModel(name='minValue', args=(0,))]
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
                        type='NumberInput', source='age',
                        params={'label': 'Age', 'min': 0},
                        validators=[ValidatorModel(name='minValue', args=(0,))]
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
    assert fields == {'name', 'sex', 'children'}

    # Exclude fields for view
    resource_admin.edit_view.fields = Exclude('sex')
    view = resource_admin.get_edit_view()
    fields = {f.source for f in view.fields}
    assert fields == {'name', 'children'}

    # Only fields for view
    resource_admin.edit_view.fields = Only('sex')
    view = resource_admin.get_edit_view()
    fields = {f.source for f in view.fields}
    assert fields == {'sex'}
