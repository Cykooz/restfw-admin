# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
from typing import List, Optional

from pyramid.registry import Registry
from pyramid.request import Request
from zope.interface import Interface

from .models import ValidatorModel
from .typing import ColanderNode, ColanderValidator
from .widgets import FieldWidget, InputWidget


class IAdminChoices(Interface):
    """Interface of utility to get list of tuples (id, name)
    with choices for some filed in admin UI.
    """

    def __call__(registry):
        """Returns list of tuples (id, name).
        :type registry: pyramid.registry.Registry
        """


class IResourceAdminFabric(Interface):

    def __call__(request: Request, name: str):
        pass


class ISchemaNodeToFieldWidget(Interface):

    def __call__(registry: Registry, node: ColanderNode) -> Optional[FieldWidget]:
        pass


class ISchemaNodeToInputWidget(Interface):

    def __call__(registry: Registry, node: ColanderNode) -> Optional[InputWidget]:
        pass


class IValidatorConverter(Interface):

    def __call__(registry: Registry, validator: ColanderValidator) -> List[ValidatorModel]:
        pass


class IColanderValidator(Interface):

    def __call__(node, value):
        pass
