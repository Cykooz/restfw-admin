# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 25.04.2020
"""
from typing import Any, Callable, Dict, List, Tuple, Union

import colander


ColanderNode = colander._SchemaNode
ColanderValidator = Callable[[ColanderNode, Any], None]
JsonNumber = Union[int, float]
SimpleJsonValue = Union[str, JsonNumber, bool]
Json = Union[SimpleJsonValue, List['Json'], Tuple['Json', ...], Dict[str, 'Json']]
