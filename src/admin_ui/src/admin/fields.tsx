import {
    ArrayField,
    ArrayInput,
    BooleanField,
    BooleanInput,
    ChipField,
    Datagrid,
    DateField,
    DateInput,
    DateTimeInput,
    FileField,
    FileInput,
    FunctionField,
    NullableBooleanInput,
    NumberField,
    NumberInput,
    ReferenceField,
    ReferenceInput,
    ReferenceManyField,
    RichTextField,
    SelectField,
    SelectInput,
    SimpleFormIterator,
    SingleFieldList,
    TextField,
    TextInput,
    UrlField,
} from 'react-admin';
import {IField} from "./apiInfo";
import {JSX, ReactElement} from "react";
import {getFieldValidators} from "./validators";
import {RichTextInput} from "ra-input-rich-text";
import {JsonField, JsonInput, MappingField, MappingInput, NestedArrayField, SimpleArrayField} from "./widgets";
import Chip from "@mui/material/Chip";

export const defaultFieldStyle = {
    // maxWidth: '18em',
    // overflow: 'hidden',
    // textOverflow: 'ellipsis',
    // whiteSpace: 'nowrap',
};


interface IFabric {
    (key: string, field: IField): JSX.Element;
}


// function view_fabric<P>(Component: FC<P>, default_props?: any) {
function view_fabric(Component: any, default_props?: any) {
    return function (key: string, field: IField) {
        return (
            <Component
                key={key}
                source={field.source}
                style={defaultFieldStyle}
                {...default_props}
                {...field.params}
            />
        );
    };
}


// function input_fabric<P>(Component: FunctionComponent<P>) {
function input_fabric(Component: any) {
    return function (key: string, field: IField) {
        const validators = getFieldValidators(field);
        return (
            <Component
                key={key}
                source={field.source}
                validate={validators}
                style={defaultFieldStyle}
                {...field.params}
            />
        );
    };
}


// Select input

function select_input_fabric(key: string, field: IField) {
    const validators = getFieldValidators(field);
    const {emptyValue, ...params} = field.params;
    const empty_value = emptyValue || '';
    return (
        <SelectInput
            key={key}
            source={field.source}
            validate={validators}
            style={defaultFieldStyle}
            emptyValue={empty_value}
            {...params}
        />
    );
}


// Array field and input

function array_view_fabric(key: string, field: IField) {
    const {fields, ...params} = field.params;
    return (
        <ArrayField
            key={key}
            source={field.source}
            {...params}
        >
            <Datagrid
                bulkActionButtons={false}
                sx={{
                    '& .RaDatagrid-headerCell': {
                        backgroundColor: '#e0e0e0',
                    },
                }}
            >
                {getFields(fields)}
            </Datagrid>
        </ArrayField>
    );
}


function array_input_fabric(key: string, field: IField) {
    const validators = getFieldValidators(field);
    const {fields, ...params} = field.params;
    return (
        <ArrayInput
            key={key}
            source={field.source}
            validate={validators}
            {...params}
        >
            <SimpleFormIterator>
                {getInputs(fields)}
            </SimpleFormIterator>
        </ArrayInput>
    );
}


// Nested array field

function nested_array_view_fabric(key: string, field: IField) {
    const {fields, single_field, ...params} = field.params;
    if (single_field) {
        return (
            <NestedArrayField
                key={key}
                source={field.source}
                {...params}
            >
                <SingleFieldList linkType={false}>
                    <Chip label={getField(single_field)}/>
                </SingleFieldList>
            </NestedArrayField>
        );
    } else {
        return (
            <NestedArrayField
                key={key}
                source={field.source}
                {...params}
            >
                <Datagrid
                    bulkActionButtons={false}
                    sx={{
                        '& .RaDatagrid-headerCell': {
                            backgroundColor: '#e0e0e0',
                        },
                    }}
                >
                    {getFields(fields)}
                </Datagrid>
            </NestedArrayField>
        );
    }
}


// Reference field and input

function referenceFieldFabric(key: string, field: IField) {
    const {child, ...params} = field.params;
    return (
        <ReferenceField
            key={key}
            source={field.source}
            {...params}
        >
            {getFieldComponent('1', child)}
        </ReferenceField>
    );
}


function referenceInputFabric(key: string, field: IField) {
    const {child, filter, ...params} = field.params;
    return (
        <ReferenceInput
            key={key}
            source={field.source}
            sort={false}
            filter={filter}
            {...params}
        >
            {getFieldComponent('1', child)}
        </ReferenceInput>
    );
}

// Mapping

function mapping_field_fabric(key: string, field: IField) {
    const {fields, ...params} = field.params;
    return (
        <MappingField
            key={key}
            source={field.source}
            {...params}
        >
            {getFields(fields)}
        </MappingField>
    );
}

function mapping_input_fabric(key: string, field: IField) {
    const {fields, ...params} = field.params;
    return (
        <MappingInput
            key={key}
            source={field.source}
            {...params}
        >
            {getInputs(fields)}
        </MappingInput>
    );
}

// File input

function file_input_fabric(key: string, field: IField) {
    return (
        <FileInput key={key} source={field.source} {...field.params}>
            <FileField source="src" title="title" />
        </FileInput>
    );
}

const COMPONENTS: Record<string, IFabric> = {
    'TextField': view_fabric(TextField),
    'RichTextField': view_fabric(RichTextField),
    'DateField': view_fabric(DateField),
    'DateTimeField': view_fabric(DateField, {showTime: true}),
    'NumberField': view_fabric(NumberField),
    'BooleanField': view_fabric(BooleanField),
    'FunctionField': view_fabric(FunctionField),
    'ReferenceManyField': view_fabric(ReferenceManyField),
    'ReferenceField': referenceFieldFabric,
    'SelectField': view_fabric(SelectField),
    'ArrayField': array_view_fabric,
    'SimpleArrayField': view_fabric(SimpleArrayField),
    'NestedArrayField': nested_array_view_fabric,
    'MappingField': mapping_field_fabric,
    'JsonField': view_fabric(JsonField),
    'ChipField': view_fabric(ChipField),
    'UrlField': view_fabric(UrlField),
    'FileField': view_fabric(FileField),
    // Inputs
    'TextInput': input_fabric(TextInput),
    'RichTextInput': view_fabric(RichTextInput),
    'DateInput': input_fabric(DateInput),
    'DateTimeInput': input_fabric(DateTimeInput),
    'NullableBooleanInput': input_fabric(NullableBooleanInput),
    'BooleanInput': input_fabric(BooleanInput),
    'NumberInput': input_fabric(NumberInput),
    'SelectInput': select_input_fabric,
    'ArrayInput': array_input_fabric,
    'ReferenceInput': referenceInputFabric,
    'MappingInput': mapping_input_fabric,
    'JsonInput': input_fabric(JsonInput),
    'FileInput': file_input_fabric,
};


function getFieldComponent(key: string, field: IField): JSX.Element {
    const fabric = COMPONENTS[field.type] || view_fabric(TextField);
    return fabric(key, field);
}


function getField(field: IField): ReactElement {
    const key = field.id ?? `field${field.id}`;
    return getFieldComponent(key, field);
}

export function getFields(fields: IField[]): ReactElement | ReactElement[] | undefined {
    const result = fields.map((field, index) => {
        const key = field.id ?? `field${index}`;
        return getFieldComponent(key, field);
    });
    if (result.length === 0) {
        return;
    } else if (result.length === 1) {
        return result[0];
    } else {
        return result;
    }
}


export function getInputs(
    fields: IField[],
    always_array = false,  // Returns an array, even if it contains a single element.
): ReactElement | ReactElement[] | undefined {
    const result = fields.map((field, index) => {
        const fabric = COMPONENTS[field.type] || input_fabric(TextInput);
        const key = field.id ?? `field${index}`;
        return fabric(key, field);
    });
    if (result.length === 0) {
        return;
    } else if (result.length === 1 && !always_array) {
        return result[0];
    } else {
        return result;
    }
}
