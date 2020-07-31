import {
    ArrayField,
    ArrayInput,
    BooleanField,
    BooleanInput,
    Datagrid,
    DateField,
    DateInput,
    DateTimeInput,
    FunctionField,
    NullableBooleanInput,
    NumberField,
    NumberInput,
    ReferenceField,
    ReferenceInput,
    ReferenceManyField,
    SelectField,
    SelectInput,
    SimpleFormIterator,
    TextField,
    TextInput,
} from 'react-admin';
import {IField} from "./apiInfo";
import React, {ComponentType} from "react";
import {getFieldValidators} from "./validators";


export const defaultFieldStyle = {
    // maxWidth: '18em',
    // overflow: 'hidden',
    // textOverflow: 'ellipsis',
    // whiteSpace: 'nowrap',
};


interface IFabric {
    (key: string, field: IField): JSX.Element;
}


function view_fabric(Component: ComponentType, default_props?: any) {
    return function(key: string, field: IField) {
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


function input_fabric(Component: ComponentType) {
    return function(key: string, field: IField) {
        let validators = getFieldValidators(field);
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


// Array field and input

function array_view_fabric(key: string, field: IField) {
    let {fields, ...params} = field.params;
    return (
        <ArrayField
            key={key}
            source={field.source}
            {...params}
        >
            <Datagrid>
                {getFields(fields)}
            </Datagrid>
        </ArrayField>
    );
}


function array_input_fabric(key: string, field: IField) {
    let validators = getFieldValidators(field);
    let {fields, ...params} = field.params;
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


// Reference field and input

function referenceFieldFabric(key: string, field: IField) {
    let {child, ...params} = field.params;
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
    let {child, ...params} = field.params;
    return (
        <ReferenceInput
            key={key}
            source={field.source}
            {...params}
        >
            {getFieldComponent('1', child)}
        </ReferenceInput>
    );
}

export const COMPONENTS: Record<string, IFabric> = {
    'TextField': view_fabric(TextField),
    // 'JsonField': {
    //   component: JsonField,
    //   props: {sortable: false},
    //   style: {},
    // },
    'DateField': view_fabric(DateField),
    'DateTimeField': view_fabric(DateField, {showTime: true}),
    'NumberField': view_fabric(NumberField),
    'BooleanField': view_fabric(BooleanField),
    'FunctionField': view_fabric(FunctionField),
    'ReferenceManyField': view_fabric(ReferenceManyField),
    'ReferenceField': referenceFieldFabric,
    'SelectField': view_fabric(SelectField),
    'ArrayField': array_view_fabric,
    // Inputs
    'TextInput': input_fabric(TextInput),
    'DateInput': input_fabric(DateInput),
    'DateTimeInput': input_fabric(DateTimeInput),
    'NullableBooleanInput': input_fabric(NullableBooleanInput),
    'BooleanInput': input_fabric(BooleanInput),
    'NumberInput': input_fabric(NumberInput),
    'SelectInput': input_fabric(SelectInput),
    'ArrayInput': array_input_fabric,
    'ReferenceInput': referenceInputFabric,
    // 'JsonInput': {
    //   component: JsonInput,
    //   props: {defaultValue: {}},
    //   style: {},
    // },
};


function getFieldComponent(key, field: IField): JSX.Element {
    let fabric = COMPONENTS[field.type] || view_fabric(TextField);
    return fabric(key, field);
}


export function getFields(fields: IField[]) {
    return fields.map((field, index) => {
        return getFieldComponent(index.toString(), field);
    });
}


export function getInputs(fields: IField[]) {
    return fields.map((field, index) => {
        let fabric = COMPONENTS[field.type] || input_fabric(TextInput);
        return fabric(index.toString(), field);
    });
}
