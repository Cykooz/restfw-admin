# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 31.07.2020
"""
import colander
from restfw import schemas
from restfw.hal import HalResource, HalResourceWithEmbedded
from restfw.interfaces import MethodOptions
from restfw.schemas import GetEmbeddedSchema

from .. import validators as all_validators, widgets as all_widgets
from ..models import FieldModel, ValidatorModel
from ..resource_admin import Exclude, ResourceAdmin, ViewSettings


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
        fields=Exclude('data'),
        widgets={
            'user_id': all_widgets.ReferenceField(
                reference='users',
                reference_field='name',
                label='User',
            )
        }
    )
    create_view = ViewSettings(
        widgets={
            'user_id': all_widgets.ReferenceInput(
                reference='users',
                option_text='name',
                label='User',
                validators=[all_validators.Required()]
            )
        }
    )


def test_reference_field_and_input(pyramid_request):
    resource_admin = DocsAdmin(pyramid_request, 'docs')
    view = resource_admin.get_list_view()
    fields = sorted(view.fields, key=lambda f: f.source)
    assert fields == [
        FieldModel(type='NumberField', source='id', params={'label': 'ID'}),
        FieldModel(
            type='ReferenceField',
            source='user_id',
            params={
                'reference': 'users',
                'label': 'User',
                'link': 'edit',
                'child': FieldModel(type='TextField', source='name', params={'label': 'Name'}),
            },
        ),
    ]

    view = resource_admin.get_create_view()
    fields = sorted(view.fields, key=lambda f: f.source)
    assert fields == [
        FieldModel(
            type='TextInput',
            source='data',
            params={'label': 'Document data'},
            validators=[ValidatorModel(name='required')],
        ),
        FieldModel(
            type='ReferenceInput',
            source='user_id',
            params={
                'reference': 'users',
                'label': 'User',
                'child': FieldModel(type='SelectInput', source=None, params={'optionText': 'name'}),
            },
            validators=[ValidatorModel(name='required')],
        )
    ]

    assert resource_admin.get_edit_view() is None
