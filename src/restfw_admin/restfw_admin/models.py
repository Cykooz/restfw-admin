# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 24.04.2020
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, TypeVar, Union

from .typing import Json


@dataclass()
class ValidatorModel:
    name: str
    args: Tuple[Json, ...] = field(default_factory=tuple)


@dataclass()
class FieldModel:
    type: str
    source: Optional[str]
    params: Dict[str, Union[Json, 'FieldModel']] = field(default_factory=dict)
    validators: List[ValidatorModel] = field(default_factory=list)


@dataclass()
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


@dataclass()
class ViewsModel:
    list: Optional[ListViewModel] = None
    show: Optional[ShowViewModel] = None
    create: Optional[CreateViewModel] = None
    edit: Optional[EditViewModel] = None


@dataclass()
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


@dataclass()
class ApiInfoModel:
    root_url: str
    title: str
    resources: Dict[str, ResourceInfoModel]
