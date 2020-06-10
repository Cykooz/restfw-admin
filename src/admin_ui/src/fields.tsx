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
                source={field.name}
                label={field.label}
                style={defaultFieldStyle}
                {...default_props}
                {...field.props}
            />
        );
    };
}


function array_view_fabric(key: string, field: IField) {
    let {sub_fields, ...props} = field.props;
    return (
        <ArrayField
            key={key}
            source={field.name}
            label={field.label}
            {...props}
        >
            <Datagrid>
                {getFields(sub_fields)}
            </Datagrid>
        </ArrayField>
    );
}


function input_fabric(Component: ComponentType) {
    return function(key: string, field: IField) {
        let validators = getFieldValidators(field);
        return (
            <Component
                key={key}
                source={field.name}
                label={field.label}
                validators={validators}
                style={defaultFieldStyle}
                {...field.props}
            />
        );
    };
}


function array_input_fabric(key: string, field: IField) {
    let validators = getFieldValidators(field);
    let {sub_fields, ...props} = field.props;
    return (
        <ArrayInput
            key={key}
            source={field.name}
            label={field.label}
            validate={validators}
            {...props}
        >
            <SimpleFormIterator>
                {getInputs(sub_fields)}
            </SimpleFormIterator>
        </ArrayInput>
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
    'ReferenceField': view_fabric(ReferenceField),
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
    // 'JsonInput': {
    //   component: JsonInput,
    //   props: {defaultValue: {}},
    //   style: {},
    // },
};


export function getFields(fields: IField[]) {
    return fields.map((field, index) => {
        let fabric = COMPONENTS[field.type] || view_fabric(TextField);
        return fabric(index.toString(), field);
    });
}


export function getInputs(fields: IField[]) {
    return fields.map((field, index) => {
        let fabric = COMPONENTS[field.type] || input_fabric(TextInput);
        return fabric(index.toString(), field);
    });
}
