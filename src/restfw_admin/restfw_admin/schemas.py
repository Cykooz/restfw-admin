# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
import colander
from restfw import schemas


class AdminChoiceSchema(schemas.ResourceSchema):
    uniq_id = schemas.StringNode(title='Unique ID')
    group = schemas.StringNode(title='Group')
    id = schemas.EmptyStringNode(
        title='ID',
        description='Choice ID that unique inside of its group',
    )
    name = schemas.EmptyStringNode(title='Name')


class AdminChoicesSchema(schemas.HalResourceWithEmbeddedSchema):
    _embedded = schemas.EmbeddedNode(
        colander.SequenceSchema(
            AdminChoiceSchema(title='Choice'),
            name='choices', title='List of embedded choices'
        ),
        missing=colander.drop
    )


class GetAdminChoicesSchema(schemas.GetEmbeddedSchema):
    group = schemas.StringNode(
        title='Choice group',
        missing=colander.drop,
    )
    id = schemas.SequenceNode(
        schemas.StringNode(title='ID'),
        title='Choices IDs', missing=colander.drop,
    )
