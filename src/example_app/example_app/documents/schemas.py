# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 31.07.2020
"""

import decimal

import colander
from restfw import schemas

from restfw_admin import widgets
from restfw_admin.schemas import FileNode
from ..users.schemas import user_id_validator


class DocMetaDataSchema(schemas.MappingNode):
    type = schemas.EmptyStringNode(title='Document type')
    custom = schemas.MappingNode(
        title='Custom data',
        unknown='preserve',
        widget=widgets.JsonField(),
    )


class EditDocMetaDataSchema(schemas.MappingNode):
    type = schemas.EmptyStringNode(title='Document type', missing='')
    custom = schemas.MappingNode(
        title='Custom data',
        unknown='preserve',
        widget=widgets.JsonInput(
            initial_value={},
            full_width=True,
        ),
    )


class DocSchema(schemas.HalResourceSchema):
    id = schemas.UnsignedIntegerNode(title='ID')
    user_id = schemas.IntegerNode(title='User ID')
    name = schemas.StringNode(title='Document name')
    data = schemas.EmptyStringNode(title='Document data')
    image = FileNode(title='Document image', nullable=True)
    publish_date = schemas.DateTimeNode(
        title='Publish date',
        nullable=True,
    )
    weight = colander.SchemaNode(
        colander.Decimal('.00', decimal.ROUND_HALF_UP),
        title='Weight',
        description='Used for documents ordering.',
    )
    meta = DocMetaDataSchema(title='Meta data')


class DocsSchema(schemas.HalResourceWithEmbeddedSchema):
    _embedded = schemas.EmbeddedNode(
        schemas.SequenceNode(
            DocSchema(title='Document'),
            name='docs',
            title='List of embedded documents',
        ),
        missing=colander.drop,
    )


class GetDocsSchema(schemas.GetEmbeddedSchema):
    name = schemas.StringNode(
        title='Document name',
        missing=colander.drop,
    )


class CreateDocSchema(schemas.MappingNode):
    user_id = schemas.IntegerNode(title='User ID', validator=user_id_validator)
    name = schemas.StringNode(title='Document name')
    data = schemas.EmptyStringNode(title='Document data')
    image = FileNode(title='Document image', nullable=True)
    meta = EditDocMetaDataSchema(title='Meta data')
    publish_date = schemas.DateTimeNode(
        title='Publish date',
        nullable=True,
        missing=None,
    )
    weight = colander.SchemaNode(
        colander.Decimal('.00', decimal.ROUND_HALF_UP),
        title='Weight',
        description='Used for documents ordering.',
        missing=decimal.Decimal('0.00'),
    )


PatchDocSchema = schemas.clone_schema_class(
    'PatchDocSchema',
    CreateDocSchema,
    excludes=['user_id'],
    nodes_missing=colander.drop,
)
