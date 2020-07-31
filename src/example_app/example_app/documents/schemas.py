# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 31.07.2020
"""
import colander
from restfw import schemas

from ..users.schemas import user_id_validator


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
    user_id = schemas.IntegerNode(title='User ID', validator=user_id_validator)
    data = schemas.EmptyStringNode(title='Document data')
