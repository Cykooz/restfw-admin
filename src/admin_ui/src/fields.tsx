import {
    BooleanField,
    DateField,
    DateInput,
    DateTimeInput,
    FunctionField,
    NullableBooleanInput,
    NumberField,
    ReferenceField,
    ReferenceManyField,
    TextField,
    TextInput,
} from 'react-admin';
import {IField} from "./apiInfo";
import React, {ComponentType} from "react";


export const defaultFieldStyle = {
    // maxWidth: '18em',
    // overflow: 'hidden',
    // textOverflow: 'ellipsis',
    // whiteSpace: 'nowrap',
};


interface FieldDescription {
    component: ComponentType;
    props: any,
    style: any;
}

export const COMPONENTS: Record<string, FieldDescription> = {
    'TextField': {
        component: TextField,
        props: {},
        style: defaultFieldStyle,
    },
    // 'JsonField': {
    //   component: JsonField,
    //   props: {sortable: false},
    //   style: {},
    // },
    'DateField': {
        component: DateField,
        props: {},
        style: defaultFieldStyle,
    },
    'DateTimeField': {
        component: DateField,
        props: {
            showTime: true,
        },
        style: defaultFieldStyle,
    },
    'NumberField': {
        component: NumberField,
        props: {},
        style: defaultFieldStyle,
    },
    'BooleanField': {
        component: BooleanField,
        props: {},
        style: defaultFieldStyle,
    },
    'FunctionField': {
        component: FunctionField,
        props: {},
        style: defaultFieldStyle,
    },
    'ReferenceManyField': {
        component: ReferenceManyField,
        props: {},
        style: defaultFieldStyle,
    },
    'ReferenceField': {
        component: ReferenceField,
        props: {},
        style: defaultFieldStyle,
    },
    'TextInput': {
        component: TextInput,
        props: {},
        style: defaultFieldStyle,
    },
    'DateInput': {
        component: DateInput,
        props: {},
        style: defaultFieldStyle,
    },
    'DateTimeInput': {
        component: DateTimeInput,
        props: {},
        style: defaultFieldStyle,
    },
    'NullableBooleanInput': {
        component: NullableBooleanInput,
        props: {},
        style: defaultFieldStyle,
    },
    // 'JsonInput': {
    //   component: JsonInput,
    //   props: {defaultValue: {}},
    //   style: {},
    // },
};


export function getFields(fields: IField[]) {
    return fields.map((field, index) => {
        let Field = COMPONENTS[field.type] || COMPONENTS.TextField;

        return (<Field.component
            key={index}
            source={field.name}
            style={Field.style}
            {...Field.props}
        />);
    });
}


export function getInputs(fields: IField[]) {
    return fields.map((field, index) => {
        let Field = COMPONENTS[field.type] || COMPONENTS.TextInput;

        return (<Field.component
            key={index}
            source={field.name}
            style={Field.style}
            {...Field.props}
        />);
    });
}
