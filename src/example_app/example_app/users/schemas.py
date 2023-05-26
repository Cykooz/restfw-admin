# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
import colander
from restfw import schemas


class Child(schemas.MappingNode):
    sex = schemas.StringNode(title='Sex', validator=colander.OneOf(['m', 'f']))
    name = schemas.StringNode(title='Name')
    age = schemas.UnsignedIntegerNode(title='Age', nullable=True)


class Work(schemas.MappingNode):
    title = schemas.StringNode(title="Title")
    address = schemas.StringNode(title="Address")


class UserSchema(schemas.HalResourceSchema):
    id = schemas.UnsignedIntegerNode(title='ID')
    created = schemas.DateTimeNode(title='Created')
    first_name = schemas.StringNode(title='First Name')
    last_name = schemas.StringNode(title='Last Name')
    age = schemas.UnsignedIntegerNode(title='Age', nullable=True)
    sex = schemas.StringNode(title='Sex', validator=colander.OneOf(['m', 'f']))
    children = schemas.SequenceNode(Child(title='Child'))
    current_work = Work(title='Current work')
    tags = schemas.SequenceNode(
        schemas.StringNode(title='Tag'),
        title='Tags'
    )


class CreateUserSchema(schemas.MappingNode):
    first_name = schemas.StringNode(
        title='First Name',
        validator=colander.All(
            colander.Length(max=50),
            colander.Regex(r'^[a-zA-z0-9]+$')
        ),
    )
    last_name = schemas.EmptyStringNode(
        title='Last Name',
        validator=schemas.NullableValidator(
            colander.All(
                colander.Length(max=50),
                colander.Regex(r'^[a-zA-z0-9]*$')
            )
        ),
        nullable=True,
    )
    age = schemas.UnsignedIntegerNode(
        title='Age', nullable=True, missing=None,
    )
    sex = schemas.StringNode(
        title='Sex',
        validator=colander.OneOf(['m', 'f']),
        nullable=True,
        missing=None,
    )
    children = schemas.SequenceNode(
        Child(title='Child', missing=colander.drop),
        missing=[],
    )
    current_work = Work(title='Current work')
    join_work_time = schemas.DateTimeNode(
        title='Join Work Time',
        nullable=True,
        # missing=None,
    )
    tags = schemas.SequenceNode(
        schemas.StringNode(title='Tag'),
        title='Tags'
    )


PatchUserSchema = schemas.clone_schema_class(
    'PatchUserSchema',
    CreateUserSchema,
    nodes_missing=colander.drop,
)


class UsersSchema(schemas.HalResourceWithEmbeddedSchema):
    _embedded = schemas.EmbeddedNode(
        schemas.SequenceNode(
            UserSchema(title='User'),
            name='users', title='List of embedded users'
        ),
        missing=colander.drop,
    )


class GetUsersSchema(schemas.GetEmbeddedSchema):
    id = schemas.UnsignedIntegerNode(
        title='User ID',
        description='Filter by user ID',
        missing=colander.drop,
    )
    sex = schemas.StringNode(
        title='Sex',
        description='Filter by user sex',
        validator=colander.OneOf(['m', 'f']),
        missing=colander.drop,
    )
    age = schemas.UnsignedIntegerNode(
        title='Age',
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
