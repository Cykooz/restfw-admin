# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
import colander
from restfw import schemas


class Child(schemas.MappingSchema):
    sex = schemas.StringNode(title='Sex', validator=colander.OneOf(['m', 'f']))
    name = schemas.StringNode(title='Name')
    age = schemas.UnsignedIntegerNode(title='Age', nullable=True)


class UserSchema(schemas.HalResourceSchema):
    id = schemas.UnsignedIntegerNode(title='ID')
    created = schemas.DateTimeNode(title='Created')
    first_name = schemas.StringNode(title='First Name')
    last_name = schemas.StringNode(title='Last Name')
    age = schemas.UnsignedIntegerNode(title='Age', nullable=True)
    sex = schemas.StringNode(title='Sex', validator=colander.OneOf(['m', 'f']))
    children = schemas.SequenceNode(Child(title='Child'))


class CreateUserSchema(schemas.MappingSchema):
    first_name = schemas.StringNode(
        title='First Name',
        validator=colander.All(
            colander.Length(max=50),
            colander.Regex(r'^[a-zA-z0-9]+$')
        ),
    )
    last_name = schemas.StringNode(
        title='Last Name',
        validator=colander.All(
            colander.Length(max=50),
            colander.Regex(r'^[a-zA-z0-9]+$')
        ),
    )
    age = schemas.UnsignedIntegerNode(
        title='Age', nullable=True, missing=colander.drop,
    )
    sex = schemas.StringNode(title='Sex', validator=colander.OneOf(['m', 'f']))
    children = schemas.SequenceNode(
        Child(title='Child', missing=colander.drop),
    )


class PatchUserSchema(schemas.MappingSchema):
    first_name = schemas.StringNode(
        title='First Name', missing=colander.drop,
        validator=colander.All(
            colander.Length(max=50),
            colander.Regex(r'^[a-zA-z0-9]+$')
        ),
    )
    last_name = schemas.StringNode(
        title='Last Name', missing=colander.drop,
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


class UsersSchema(schemas.HalResourceWithEmbeddedSchema):
    _embedded = schemas.EmbeddedNode(
        schemas.SequenceNode(
            UserSchema(title='User'),
            name='users', title='List of embedded users'
        ),
        missing=colander.drop,
    )


@colander.deferred
def user_id_validator(_, kw):
    users = kw['request'].root['users']

    def validator(node, value: int):
        try:
            users[str(value)]
        except KeyError:
            raise colander.Invalid(node, msg='User has not found')

    return validator
