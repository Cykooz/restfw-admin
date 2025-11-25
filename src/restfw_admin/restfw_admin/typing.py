# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 25.04.2020
"""

from typing import Any, Callable

import colander


ColanderNode = colander._SchemaNode
ColanderValidator = Callable[[ColanderNode, Any], None]
