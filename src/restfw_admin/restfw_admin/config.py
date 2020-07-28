# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from dataclasses import dataclass
from typing import Optional, Type, Union

import venusian
from pyramid.config import Configurator
from pyramid.registry import Registry

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


def add_resource_admin(config: Configurator, fabric: Union[Type[ResourceAdmin], str], name: str):
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


class resource_admin_config(object):
    """ A function, class or method :term:`decorator` which allows a
    developer to create resource admin config registrations nearer to it
    definition than use :term:`imperative configuration` to do the same.

    For example, this code in a module ``admin.py``::

        @resource_admin_config(name='users')
        class UsersAdmin(ResourceAdmin):
            ...

    Might replace the following call to the
    :meth:`restfw.config.add_resource_admin` method::

       from .admin import UsersAdmin
       config.add_resource_admin(UsersAdmin, name='users')

    Two additional keyword arguments which will be passed to the
    :term:`venusian` ``attach`` function are ``_depth`` and ``_category``.

    ``_depth`` is provided for people who wish to reuse this class from another
    decorator. The default value is ``0`` and should be specified relative to
    the ``view_config`` invocation. It will be passed in to the
    :term:`venusian` ``attach`` function as the depth of the callstack when
    Venusian checks if the decorator is being used in a class or module
    context. It's not often used, but it can be useful in this circumstance.

    ``_category`` sets the decorator category name. It can be useful in
    combination with the ``category`` argument of ``scan`` to control which
    views should be processed.

    See the :py:func:`venusian.attach` function in Venusian for more
    information about the ``_depth`` and ``_category`` arguments.

    .. warning::

        ``sub_resource`` will work ONLY on module top level members
        because of the limitation of ``venusian.Scanner.scan``.

    """
    venusian = venusian  # for testing injection

    def __init__(self, name, _depth=0, _category='restfw-admin'):
        self.name = name
        self.depth = _depth
        self.category = _category

    def register(self, scanner, name, wrapped):
        config = scanner.config
        config.add_resource_admin(wrapped, self.name)

    def __call__(self, wrapped):
        self.venusian.attach(wrapped, self.register, category=self.category,
                             depth=self.depth + 1)
        return wrapped


@dataclass()
class JsFunction:
    name: str
    code: str


@dataclass()
class AdminUiSettings:
    index_html_tpl: str = ''
    auth_provider: Optional[JsFunction] = None
    http_client: Optional[JsFunction] = None


def get_admin_ui_settings(registry: Registry) -> AdminUiSettings:
    return registry.setdefault('admin_ui', AdminUiSettings())


def add_restfw_admin_auth_provider(config: Configurator, js_name: str, js_code: str):
    ui_settings = get_admin_ui_settings(config.registry)
    ui_settings.auth_provider = JsFunction(js_name, js_code)


def add_restfw_admin_http_client(config: Configurator, js_name: str, js_code: str):
    ui_settings = get_admin_ui_settings(config.registry)
    ui_settings.http_client = JsFunction(js_name, js_code)
