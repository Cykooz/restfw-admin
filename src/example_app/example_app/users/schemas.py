# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
import colander
from restfw import schemas


class UserSchema(schemas.HalResourceSchema):
    id = schemas.UnsignedIntegerNode(title='ID')
    name = schemas.StringNode(title='Name')
    created = schemas.DateTimeNode(title='Created')


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
        title='Name', validator=colander.Length(max=50),
    )
