# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
import venusian
from mountbit.utils import Enum
import inspect

from .interfaces import IAdminChoices


# FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
# ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')
#
#
# def convert_to_snake_case(name):
#     tmp = FIRST_CAP_RE.sub(r'\1_\2', name)
#     return ALL_CAP_RE.sub(r'\1_\2', tmp).lower()


class admin_choices_config(object):
    """A function, class or method :term:`decorator` which allows a
    developer to register adapter for IAdminChoices interface.

    Example, this code in a module ``interfaces.py``::

        @admin_choices_config()
        class OrderStatus(Enum):
            running = 'running'
            completed = 'completed'
            canceled = 'canceled'

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
        if inspect.isclass(wrapped) and issubclass(wrapped, Enum):
            def factory(request):
                return ((value, value.title()) for value in wrapped.enum_values())
        else:
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
