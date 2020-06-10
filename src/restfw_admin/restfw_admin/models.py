# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 24.04.2020
"""
from __future__ import annotations

import dataclasses
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

from .utils import slug_to_title


_ArgsType = Union[str, bool, int, float, list, tuple, dict]


@dataclasses.dataclass()
class ValidatorModel:
    name: str
    args: Tuple[_ArgsType, ...] = dataclasses.field(default_factory=list)

    def __init__(self, name: str, *args: _ArgsType):
        self.name = name
        self.args = args


@dataclasses.dataclass()
class FieldModel:
    type: str
    name: str
    label: str = ''
    validators: List[ValidatorModel] = dataclasses.field(default_factory=list)
    props: Dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        if not self.label:
            self.label = slug_to_title(self.name)


@dataclasses.dataclass()
class ViewModel:
    fields: List[FieldModel]


class ListViewModel(ViewModel):
    pass


class ShowViewModel(ViewModel):
    pass


class CreateViewModel(ViewModel):
    pass


class EditViewModel(ViewModel):
    pass


ViewModelType = TypeVar('ViewModelType', ListViewModel, ShowViewModel, CreateViewModel, EditViewModel)


@dataclasses.dataclass()
class ViewsModel:
    list: Optional[ListViewModel] = None
    show: Optional[ShowViewModel] = None
    create: Optional[CreateViewModel] = None
    edit: Optional[EditViewModel] = None


@dataclasses.dataclass()
class ResourceInfoModel:
    index: int
    name: str
    title: str
    location: str
    id_field: str
    embedded_name: str
    update_method: str
    deletable: bool
    views: ViewsModel


@dataclasses.dataclass()
class ApiInfoModel:
    root_url: str
    title: str
    resources: Dict[str, ResourceInfoModel]
