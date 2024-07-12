import {TextInput, TextInputProps} from 'react-admin';

const DEFAULT_ERRORTEXT = "Invalid JSON";

export interface JsonInputProps
    extends TextInputProps {
    indent_width?: number;
    error_text?: string;
    parse_json?: boolean;
}

/**
 *
 * `JsonInput` validates if the entered value is JSON or not. If entered value is not a invalid JSON, `JsonInput` will throw an error.
 * Default error message is: `Invalid JSON` and can be overridden using `errortext` prop.
 *
 * @example
 * <JsonInput source='config' label='JSON Config' errortext='Enter a valid JSON'/>
 *
 * or use translate function:
 *
 * @example
 * <JsonInput source='config' label={translate('resources.resource_name.fields.config')}
 * errortext={translate('myroot.validate.json')}/>
 *
 * By default, `JsonInput` parses and returns the entered string as object.
 * Instead, to send string directly, please pass `parse_json` prop as `false`
 *
 * @example
 * <JsonInput source='config' label='JSON Config' parse_json={false}/>
 */
export const JsonInput = (props: JsonInputProps) => {
    const {
        indent_width = 2,
        error_text = DEFAULT_ERRORTEXT,
        parse_json = true,
        ...base_props
    } = props;
    const validateJSON = (value: any) => {
        if (!value || typeof value === 'object')
            return undefined;
        return isJSON(value) ? undefined : error_text;
    }

    let last_value: string | null = null;

    const parse_function = (json: any): any => {
        last_value = json;
        try {
            let retval = json;
            if (retval && typeof retval === 'object')
                retval = JSON.stringify(retval, null_replacer);
            retval = JSON.parse(retval);
            return retval;
        } catch (e) {
            return json;
        }
    };

    const format_json = (json: any): string => {
        if (last_value !== null) {
            return last_value;
        }
        let retval = json;
        if (retval && typeof retval === 'object')
            retval = JSON.stringify(retval, null, indent_width);
        last_value = retval;
        return retval;
    };

    const input_props = {
        ...base_props,
        format: format_json,
        parse: (parse_json ? parse_function : undefined)
    };
    if (input_props.validate === undefined) {
        input_props.validate = [validateJSON];
    } else if (Array.isArray(input_props.validate)) {
        input_props.validate.push(validateJSON);
    } else {
        input_props.validate = [input_props.validate, validateJSON];
    }

    return (
        <TextInput {...input_props}/>
    );
}


function null_replacer(key: any, val: any): undefined | any {
    return val === null ? undefined : val
}

function assert_string(input: any) {
    const isString = typeof input === 'string' || input instanceof String;

    if (!isString) {
        let invalidType: string = typeof input;
        if (input === null) invalidType = "null";
        else if (invalidType === 'object') invalidType = input.constructor.name;

        throw new TypeError(`Expected a string but received a ${invalidType}`);
    }
}

function isJSON(str: any) {
    assert_string(str);
    try {
        const primitives: any[] = [null, false, true];
        const obj = JSON.parse(str);
        return primitives.includes(obj) || (!!obj && typeof obj === 'object');
    } catch (e) {
        /* ignore */
    }
    return false;
}
