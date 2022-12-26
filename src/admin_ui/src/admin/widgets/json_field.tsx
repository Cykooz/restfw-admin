import React from "react";
import {FunctionField, useRecordContext} from 'react-admin';
import {RaRecord} from "ra-core";
import {InjectedFieldProps, PublicFieldProps} from "ra-ui-materialui/src/field/types";

const ViewJSON = (JsonObj: any, indent_width: number) => {
    if (JsonObj === JSON.stringify({})) return '';
    if (JsonObj && typeof JsonObj === 'object')
        JsonObj = JSON.stringify(JsonObj, null, indent_width);
    return <pre>{JsonObj}</pre>;
}
function get_json(record: RaRecord | undefined, source: string): any {
    if (record) {
        return record[source];
    }
    return "";
}


export interface JsonFieldProps
    extends PublicFieldProps,
        InjectedFieldProps {
    json?: string | object;
    indent_width?: number;
}

export const JsonField = (props: JsonFieldProps) => {
    const {
        indent_width = 2,
        json,
        source,
    } = props;
    const record = useRecordContext();
    if (!json && !source) throw new Error(`Missing mandatory prop: json or source`);
    const data = json || get_json(record, source || '');
    if (!data) return null;

    const retVal = (
        <div>
            {ViewJSON(data, indent_width)}
        </div>
    );
    return (
        <FunctionField render={() => retVal}/>
    );
}

export default JsonField;
