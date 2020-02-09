# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from zope.interface import Interface


class IAdminResourceFabric(Interface):

    def __call__(request):
        """Returns JS code which registers resources in the ``ng-admin``."""


class IAdminReactResourceFabric(Interface):

    def __call__(request):
        """Returns JS code which registers resources in the ``react-admin``."""


class IAdminReactResources(Interface):

    def sorted():
        """Returns the sorted list of tuples (name, fabric) in topologically sorted order."""


class IAdminChoices(Interface):
    """Interface of utility to get list of tuples (id, name)
    with choices for some filed in admin UI.
    """

    def __call__(request):
        """Returns list of tuples (id, name).
        :type request: pyramid.request.Request
        """
