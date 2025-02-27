# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 04.07.2020
"""

from dataclasses import dataclass, field, fields
from typing import Any, ClassVar, Dict, List, Literal, Optional, Tuple, Union

from restfw.typing import Json, JsonNumber, SimpleJsonValue

from .models import FieldModel
from .utils import slug_to_title
from .validators import Validator


def ra_field(name, **kwargs):
    """Helper function to create a field of widget with information
    about a real name of property of widget from ReactAdmin."""
    if 'default_factory' not in kwargs:
        kwargs.setdefault('default', None)
    return field(metadata={'ra_name': name}, **kwargs)


@dataclass()
class Widget:
    type: ClassVar[str]
    label: Optional[str] = None
    # A class name (usually generated by JSS) to customize
    # the look and feel of the field element itself.
    css_class: Optional[str] = ra_field('className')
    # A class name (usually generated by JSS) to customize
    # the look and feel of the field container when it is
    # used inside <SimpleForm> or <TabbedForm>.
    form_css_class: Optional[str] = ra_field('formClassName')

    def to_model(self, field_name: Optional[str]) -> FieldModel:
        params = {}
        for f in fields(self):
            value = getattr(self, f.name)
            if value is None:
                continue
            name = f.metadata.get('ra_name', f.name)
            params[name] = value
        if 'label' not in params and field_name:
            params['label'] = slug_to_title(field_name)
        return FieldModel(type=self.type, source=field_name, params=params)

    def get_fields(self) -> Dict[str, Any]:
        return {
            f.name: value
            for f in fields(self)
            if (value := getattr(self, f.name)) is not None
        }


@dataclass()
class FieldWidget(Widget):
    # When used in a List, should the list be sortable using
    # the source attribute? Setting it to false disables
    # the click handler on the column header.
    sortable: Optional[bool] = None
    # When used in a List, specifies the actual source to be
    # used for sorting when the user clicks the column header.
    sort_by: Optional[str] = ra_field('sortBy')
    # A class name (usually generated by JSS) to customize
    # the look and feel of the field container (e.g. the <td>
    # in a Datagrid).
    cell_css_class: Optional[str] = ra_field('cellClassName')
    # A class name (usually generated by JSS) to customize
    # the look and feel of the field header (e.g. the <th>
    # in a Datagrid).
    header_css_class: Optional[str] = ra_field('headerClassName')
    # Defines the visibility of the label when the field is
    # used in <SimpleForm>, <FormTab>, <SimpleShowLayout>,
    # or <Tab>. It’s true for all react-admin <Field> components.
    add_label: Optional[bool] = ra_field('addLabel')
    # Defines the text alignment inside a cell. Set to right
    # for right alignment (e.g. for numbers).
    text_align: Optional[Literal['left', 'right']] = ra_field('textAlign')
    # Defines a text to be shown when a field has no value
    empty_text: Optional[str] = ra_field('addLabel')


@dataclass()
class InputWidget(Widget):
    # Value to be set when the property is undefined.
    default_value: Optional[Json] = ra_field('defaultValue')
    # Validation rules for the current property.
    validators: Optional[List[Validator]] = None
    # Text to be displayed under the input (cannot be used inside a filter)
    helper_text: Optional[str] = ra_field('helperText')
    # If true, the input will expand to fill the form width.
    full_width: Optional[bool] = ra_field('fullWidth')

    def to_model(self, field_name: str) -> FieldModel:
        field_model = super().to_model(field_name)
        if self.validators:
            field_model.validators = [v.to_model() for v in self.validators]
        field_model.params.pop('validators', None)
        return field_model


class TextField(FieldWidget):
    type = 'TextField'


@dataclass()
class TextInput(InputWidget):
    type = 'TextInput'
    # If True, display a button to reset the changes in this input value.
    resettable: Optional[bool] = None
    # Type attribute passed to the <input> element.
    input_type: Optional[str] = ra_field('type')
    multiline: Optional[bool] = None


@dataclass()
class RichTextField(FieldWidget):
    type = 'RichTextField'
    # If true, remove all HTML tags and render text only
    strip_tags: Optional[bool] = ra_field('stripTags')


class RichTextInput(FieldWidget):
    type = 'RichTextInput'


@dataclass()
class NumberField(FieldWidget):
    type = 'NumberField'
    # Override the browser locale that used for formatting.
    # Passed as first argument to Intl.NumberFormat().
    locales: Optional[str] = None
    # Number formatting options. Passed as second argument.
    # to Intl.NumberFormat().
    options: Optional[Dict[str, SimpleJsonValue]] = None

    def __post_init__(self):
        if not self.options or 'useGrouping' not in self.options:
            # Disable thousands grouping by default
            self.options = self.options or {}
            self.options['useGrouping'] = False


@dataclass()
class NumberInput(InputWidget):
    type = 'NumberInput'
    # The maximum value to accept for this input.
    max: Optional[JsonNumber] = None
    # The minimum value to accept for this input.
    min: Optional[JsonNumber] = None
    # A stepping interval to use when using up and down
    # arrows to adjust the value, as well as for validation
    step: Optional[JsonNumber] = None


class BooleanField(FieldWidget):
    type = 'BooleanField'


class BooleanInput(InputWidget):
    type = 'BooleanInput'


class NullableBooleanInput(InputWidget):
    type = 'NullableBooleanInput'


@dataclass()
class DateField(FieldWidget):
    type = 'DateField'
    # Override the browser locale in the date formatting.
    # Passed as first argument to Intl.DateTimeFormat().
    locales: Optional[str] = None
    # Date formatting options. Passed as second argument
    # to Intl.DateTimeFormat().
    options: Optional[Dict[str, SimpleJsonValue]] = None
    # If True, show date and time. If False, show only date.
    show_time: Optional[bool] = ra_field('showTime')


class DateInput(InputWidget):
    type = 'DateInput'


class DateTimeInput(InputWidget):
    type = 'DateTimeInput'


class UrlField(FieldWidget):
    type = 'UrlField'


class EmailField(FieldWidget):
    type = 'EmailField'


class ChipField(FieldWidget):
    type = 'ChipField'


@dataclass()
class ChoicesWidget(Widget):
    choices: Union[List[str], List[Tuple[SimpleJsonValue, str]]] = None

    def to_model(self, field_name: Optional[str]) -> FieldModel:
        field_model = super().to_model(field_name)
        if self.choices is not None and len(self.choices) > 0:
            if isinstance(self.choices[0], (tuple, list)):
                field_model.params['choices'] = [
                    {'id': _id, 'name': name} for _id, name in self.choices
                ]
            else:
                field_model.params['choices'] = self.choices.copy()
        return field_model


class ChoicesFieldWidget(ChoicesWidget, FieldWidget):
    pass


@dataclass()
class SelectField(ChoicesFieldWidget):
    type = 'SelectField'
    # Name of the field to use to display the matching choice,
    # or function returning that field name, or a React element
    # to render for that choice.
    option_text: Optional[str] = ra_field('optionText')


class ChoicesInputWidget(ChoicesWidget, InputWidget):
    pass


@dataclass()
class SelectInput(ChoicesInputWidget):
    type = 'SelectInput'
    # If the input isn’t required, users can select an empty choice
    # with an empty_text as label and empty_value as value.
    # Overwrite value of "empty value".
    empty_value: Optional[SimpleJsonValue] = ra_field('emptyValue', default='')
    # The text to display for the empty option.
    empty_text: Optional[str] = ra_field('emptyText')
    # Props to pass to the underlying <SelectInput> element
    options: Optional[Dict[str, SimpleJsonValue]] = None
    # Field name of record to display in the suggestion item.
    option_text: Optional[str] = ra_field('optionText')
    resettable: Optional[bool] = None

    def to_model(self, field_name: Optional[str]) -> FieldModel:
        field_model = super().to_model(field_name)
        if 'emptyValue' not in field_model.params:
            field_model.params['emptyValue'] = None
        elif field_model.params['emptyValue'] == '':
            del field_model.params['emptyValue']
        return field_model


class SelectArrayInput(SelectInput):
    type = 'SelectArrayInput'


@dataclass()
class ArrayField(FieldWidget):
    type = 'ArrayField'
    fields: Dict[str, FieldWidget] = None

    # # Name for the field to be used as key when displaying children.
    # key: Optional[str] = ra_field('fieldKey')

    def __post_init__(self):
        if self.fields is None:
            raise TypeError("__init__() missing 1 required argument: 'fields'")

    def to_model(self, field_name: str) -> FieldModel:
        field_model = super().to_model(field_name)
        field_model.params['fields'] = [
            widget.to_model(name) for name, widget in self.fields.items()
        ]
        return field_model


@dataclass()
class ArrayInput(InputWidget):
    type = 'ArrayInput'
    fields: Dict[str, InputWidget] = None
    disable_add: Optional[bool] = ra_field('disableAdd')
    disable_remove: Optional[bool] = ra_field('disableRemove')

    # # Name for the field to be used as key when displaying children.
    # key: Optional[str] = ra_field('fieldKey')

    def __post_init__(self):
        if self.fields is None:
            raise TypeError("__init__() missing 1 required argument: 'fields'")

    def to_model(self, field_name: str) -> FieldModel:
        field_model = super().to_model(field_name)
        field_model.params['fields'] = [
            widget.to_model(name) for name, widget in self.fields.items()
        ]
        return field_model


@dataclass()
class SimpleArrayField(FieldWidget):
    type = 'SimpleArrayField'
    break_lines: bool = False


@dataclass()
class NestedArrayField(FieldWidget):
    type = 'NestedArrayField'
    fields: Dict[str, FieldWidget] = None
    single_field: bool = False

    def __post_init__(self):
        if self.fields is None and self.single_field is None:
            raise TypeError("__init__() missing 1 required argument: 'fields'")

    def to_model(self, field_name: str) -> FieldModel:
        field_model = super().to_model(field_name)
        if self.single_field:
            field_model.params['fields'] = None
            first_field = list(self.fields.values())[0]
            field_model.params['single_field'] = first_field.to_model('_value')
        else:
            field_model.params['fields'] = [
                widget.to_model(name) for name, widget in self.fields.items()
            ]
            field_model.params['single_field'] = None
        return field_model


@dataclass()
class ReferenceFieldBase:
    reference: str
    reference_field: str


@dataclass()
class ReferenceField(FieldWidget, ReferenceFieldBase):
    type = 'ReferenceField'
    widget: FieldWidget = field(default_factory=TextField)
    link: Literal['edit', 'show'] = 'edit'

    def to_model(self, field_name: str) -> FieldModel:
        model = super().to_model(field_name)
        del model.params['reference_field']
        del model.params['widget']
        model.params['child'] = self.widget.to_model(self.reference_field)
        return model


@dataclass()
class ReferenceInputBase:
    reference: str


@dataclass()
class ReferenceInput(InputWidget, ReferenceInputBase):
    type = 'ReferenceInput'
    # Default is SelectInput
    widget: Optional[ChoicesInputWidget] = None
    # If True, add an empty item to the list of choices to allow for empty value
    allow_empty: Optional[bool] = ra_field('allowEmpty')
    per_page: Optional[int] = ra_field('perPage', default=500)
    # Field name of record to display in the default SelectInput widget.
    option_text: Optional[str] = ra_field('optionText')

    def to_model(self, field_name: str) -> FieldModel:
        model = super().to_model(field_name)
        widget = model.params.pop('widget', None)
        option_text = model.params.pop('optionText', None)
        if not widget:
            widget = SelectInput(option_text=option_text)
        model.params['child'] = widget.to_model(field_name=None)
        return model


@dataclass()
class DynSelectBase:
    group: str


@dataclass()
class DynSelectField(FieldWidget, DynSelectBase):
    """It is SelectFiled with choices that dynamically loads
    from AdminChoices resource."""

    type = 'ReferenceField'

    def to_model(self, field_name: str) -> FieldModel:
        model = super().to_model(field_name)
        model.params['reference'] = 'admin_choices'
        model.params['queryOptions'] = {
            'meta': {
                'filter': {
                    'group': model.params.pop('group'),
                }
            }
        }
        model.params['child'] = TextField().to_model(field_name='name')
        return model


@dataclass()
class DynSelectInput(InputWidget, DynSelectBase):
    """It is SelectInput with choices that dynamically loads
    from AdminChoices resource."""

    type = 'ReferenceInput'
    # If True, add an empty item to the list of choices to allow for empty value
    allow_empty: Optional[bool] = ra_field('allowEmpty')
    per_page: Optional[int] = ra_field('perPage')

    def to_model(self, field_name: str) -> FieldModel:
        model = super().to_model(field_name)
        model.params['reference'] = 'admin_choices'
        model.params['filter'] = {'group': model.params.pop('group')}
        widget = SelectInput(option_text='name')
        model.params['child'] = widget.to_model(field_name=None)
        return model


# Mapping


@dataclass()
class MappingField(Widget):
    type = 'MappingField'
    fields: Dict[str, FieldWidget] = None

    def __post_init__(self):
        if self.fields is None:
            raise TypeError("__init__() missing 1 required argument: 'fields'")

    def to_model(self, field_name: str) -> FieldModel:
        field_model = super().to_model(field_name)
        field_model.params['fields'] = [
            widget.to_model(name) for name, widget in self.fields.items()
        ]
        return field_model


@dataclass()
class MappingInput(InputWidget):
    type = 'MappingInput'
    fields: Dict[str, InputWidget] = None

    def __post_init__(self):
        if self.fields is None:
            raise TypeError("__init__() missing 1 required argument: 'fields'")

    def to_model(self, field_name: str) -> FieldModel:
        field_model = super().to_model(field_name)
        field_model.params['fields'] = [
            widget.to_model(name) for name, widget in self.fields.items()
        ]
        return field_model


# Json


@dataclass()
class JsonField(FieldWidget):
    type = 'JsonField'
    # The indent-width for nested objects
    indent_width: Optional[int] = 2
    collapsed: bool = False
    # Set as empty sting for disable expand button
    expand_label: Optional[str] = None
    # Set as empty sting for disable expand button
    collapse_label: Optional[str] = None


@dataclass()
class JsonInput(TextInput):
    type = 'JsonInput'
    # The indent-width for nested objects, default: 2
    indent_width: Optional[int] = None
    error_text: Optional[str] = None
    # Set to False if the value is a string in JSON format, default: True
    parse_json: bool = True
    multiline: Optional[bool] = True


# File


@dataclass()
class FileField(FieldWidget):
    type = 'FileField'
    # Relative path to a source of file URL
    url_source: Optional[str] = None
    # Points to the file title property, used for title attributes.
    # It can either be a hard-written string or a path within your JSON object.
    title: Optional[str] = None
    # The link target. Set to “_blank” to open the file on a new tab
    target: Optional[str] = None
    # Prompts the user to save the linked URL instead of navigating to it
    download: None | bool | str = None
    # A space-separated list of URLs. When the link is followed,
    # the browser will send POST requests with the body PING to the URLs.
    # Typically for tracking.
    ping: Optional[str] = None
    # The relationship of the linked URL as space-separated link
    # types (e.g. 'noopener', 'canonical', etc.).
    rel: Optional[str] = None

    def to_model(self, field_name: Optional[str]) -> FieldModel:
        model = super().to_model(field_name)
        if field_name and self.url_source:
            model.source = f'{field_name}.{self.url_source}'
            if self.title:
                model.params['title'] = f'{field_name}.{self.title}'
            del model.params['url_source']
        return model


@dataclass()
class FileInput(InputWidget):
    type = 'FileInput'
    # Accepted file type(s). When empty, all file types are accepted.
    # Examples:
    #   '.doc,.docx'
    #   'application/json,video/*'
    #   'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    accept: Optional[str] = None
    # Minimum file size (in bytes)
    min_size: int = ra_field('minSize', default=0)
    # Minimum file size (in bytes)
    max_size: Optional[int] = ra_field('maxSize')
    # Additional options passed to react-dropzone’s useDropzone() hook.
    options: Optional[dict[str, Json]] = None
