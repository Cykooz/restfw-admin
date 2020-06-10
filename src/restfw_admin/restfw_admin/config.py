# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from typing import Type, Union

import venusian
from pyramid.config import Configurator

from . import interfaces
from .interfaces import IAdminChoices
from .resource_admin import ResourceAdmin


class admin_choices_config(object):
    """A function, class or method :term:`decorator` which allows a
    developer to register adapter for IAdminChoices interface.

    Example, this code in a module ``interfaces.py``::

        @admin_choices_config('product_types')
        def get_product_types(request):
            return [
                ('contacts', 'Contacts'),
                ('backup', 'Backup'),
                ('family_storage', 'Family Storage'),
            ]

    Two additional keyword arguments which will be passed to the
    :term:`venusian` ``attach`` function are ``_depth`` and ``_category``.

    ``_depth`` is provided for people who wish to reuse this class from another
    decorator. The default value is ``0`` and should be specified relative to
    the ``admin_choices_config`` invocation. It will be passed in to the
    :term:`venusian` ``attach`` function as the depth of the callstack when
    Venusian checks if the decorator is being used in a class or module
    context. It's not often used, but it can be useful in this circumstance.

    ``_category`` sets the decorator category name. It can be useful in
    combination with the ``category`` argument of ``scan`` to control which
    resource examples fabric should be processed.

    See the :py:func:`venusian.attach` function in Venusian for more
    information about the ``_depth`` and ``_category`` arguments.

    .. warning::

        ``admin_choices_config`` will work ONLY on module top level members
        because of the limitation of ``venusian.Scanner.scan``.
    """
    venusian = venusian  # for testing injection

    def __init__(self, name=None, **kwargs):
        self.name = name
        self.depth = kwargs.pop('_depth', 0)
        self.category = kwargs.pop('_category', 'provisioner_admin')

    def register(self, scanner, name, wrapped):
        config = scanner.config
        factory = wrapped

        config.registry.registerUtility(
            factory,
            IAdminChoices,
            name=self.name
        )

    def __call__(self, wrapped):
        if not self.name:
            self.name = wrapped.__name__
        self.venusian.attach(wrapped, self.register, category=self.category,
                             depth=self.depth + 1)
        return wrapped


def add_resource_admin(config: Configurator, name: str, fabric: Union[Type[ResourceAdmin], str]):
    dotted = config.maybe_dotted
    fabric = dotted(fabric)
    #verifyObject(interfaces.IExternalLinkFabric, fabric, tentative=True)

    # if not isinstance(resource_type, (tuple, list)):
    #     resource_type = (resource_type,)

    intr = config.introspectable(
        category_name='restfw_resource_admin',
        discriminator=id(fabric),
        title=config.object_description(fabric),
        type_name='restfw_resource_admin',
    )
    intr['fabric'] = fabric

    def register():
        config.registry.registerUtility(
            fabric,
            provided=interfaces.IResourceAdminFabric,
            name=name,
        )

    config.action(None, register, introspectables=(intr,))
    return fabric
