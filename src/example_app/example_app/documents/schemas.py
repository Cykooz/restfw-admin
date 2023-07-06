# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 31.07.2020
"""
import colander
from restfw import schemas

from ..users.schemas import user_id_validator


class DocMetaDataSchema(schemas.MappingNode):
    type = schemas.EmptyStringNode(title='Document type')
    custom = schemas.MappingNode(title='Custom data', unknown='preserve')


class EditDocMetaDataSchema(schemas.MappingNode):
    type = schemas.EmptyStringNode(title='Document type', missing='')
    custom = schemas.MappingNode(title='Custom data', unknown='preserve')


class DocSchema(schemas.HalResourceSchema):
    id = schemas.UnsignedIntegerNode(title='ID')
    user_id = schemas.IntegerNode(title='User ID')
    data = schemas.EmptyStringNode(title='Document data')
    publish_date = schemas.DateTimeNode(
        title='Publish date', nullable=True,
    )
    meta = DocMetaDataSchema(title='Meta data')


class DocsSchema(schemas.HalResourceWithEmbeddedSchema):
    _embedded = schemas.EmbeddedNode(
        schemas.SequenceNode(
            DocSchema(title='Document'),
            name='docs', title='List of embedded documents'
        ),
        missing=colander.drop,
    )


class CreateDocSchema(schemas.MappingNode):
    user_id = schemas.IntegerNode(title='User ID', validator=user_id_validator)
    data = schemas.EmptyStringNode(title='Document data')
    meta = EditDocMetaDataSchema(title='Meta data')
    publish_date = schemas.DateTimeNode(
        title='Publish date', nullable=True,
        missing=None,
    )


PatchDocSchema = schemas.clone_schema_class(
    'PatchDocSchema', CreateDocSchema,
    excludes=['user_id'],
    nodes_missing=colander.drop,
)
