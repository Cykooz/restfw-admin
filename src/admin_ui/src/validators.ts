import {
    required,
    minLength,
    maxLength,
    minValue,
    maxValue,
    number,
    regex,
    email,
    choices
} from 'react-admin';
import {IField} from "./apiInfo";


function create_regex(pattern: string) {
    const re = new RegExp(pattern);
    return regex(re);
}


const VALIDATORS: Record<string, any> = {
    'required': required,
    'min_value': minValue,
    'max_value': maxValue,
    'min_length': minLength,
    'max_length': maxLength,
    'is_number': number,
    'is_email': email,
    'regex': create_regex,
    'choices': choices,
};


export function getFieldValidators(field: IField) {
    return field.validators.map((validator, index) => {
        if (validator.name in VALIDATORS) {
            return VALIDATORS[validator.name].apply(undefined, validator.args);
        }
        return null;
    }).filter((validator) => {
        return validator !== null
    });
}
