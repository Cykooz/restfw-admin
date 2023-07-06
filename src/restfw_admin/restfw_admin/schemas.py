# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
import colander
from restfw import schemas


class AdminChoiceSchema(schemas.ResourceSchema):
    uniq_id = schemas.StringNode(title='Unique ID of choice')
    group = schemas.StringNode(title='Choice group')
    id = schemas.EmptyStringNode(title='Choice ID')
    name = schemas.EmptyStringNode(title='Choice name')


class AdminChoicesSchema(schemas.HalResourceWithEmbeddedSchema):
    _embedded = schemas.EmbeddedNode(
        colander.SequenceSchema(
            AdminChoiceSchema(title='Choice'),
            name='choices', title='List of embedded choices'
        ),
        missing=colander.drop
    )


class GetAdminChoicesSchema(schemas.GetEmbeddedSchema):
    group = schemas.StringNode(title='Filter by choice group', missing=colander.drop)
    id = schemas.SequenceNode(
        schemas.StringNode(title='Choice ID'),
        title='Filter by choices IDs', missing=colander.drop,
    )
