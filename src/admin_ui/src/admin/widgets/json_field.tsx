import React from "react";
import {FunctionField, Link, useRecordContext} from 'react-admin';
import {RaRecord} from "ra-core";
import {FieldProps} from "ra-ui-materialui/src/field/types";
import SyntaxHighlighter from 'react-syntax-highlighter';
import {qtcreatorLight} from 'react-syntax-highlighter/dist/esm/styles/hljs';
import get from "lodash/get";

const ViewJSON = (JsonObj: any, indent_width: number, expand: boolean) => {
    if (JsonObj === JSON.stringify({})) return '';
    if (JsonObj && typeof JsonObj === "object")
        if (expand) {
            JsonObj = JSON.stringify(JsonObj, null, indent_width);
            return (
                <SyntaxHighlighter
                    language="json"
                    style={qtcreatorLight}
                    customStyle={{marginTop: 0}}
                >
                    {JsonObj}
                </SyntaxHighlighter>
            );
        } else
            return "";
}

function get_json(record: RaRecord | undefined, source: string): any {
    if (record) {
        return get(record, source);
    }
    return "";
}


export interface JsonFieldProps
    extends FieldProps {
    json?: string | object;
    indent_width?: number;
    collapsed?: boolean;
    expand_label?: string;
    collapse_label?: string;
}

export const JsonField = (props: JsonFieldProps) => {
    const {
        indent_width = 2,
        json,
        source,
        collapsed = false,
        expand_label = "expand...",
        collapse_label = "collapse",
    } = props;
    const [expand, setExpand] = React.useState(!collapsed);
    const record = useRecordContext();
    if (!json && !source) throw new Error(`Missing mandatory prop: json or source`);
    const data = json || get_json(record, source || '');
    if (!data && typeof data !== 'object') {
        return null;
    }
    let expand_btn;
    if (expand_label && collapse_label)
        expand_btn = (
            <Link
                to="#"
                onClick={() => setExpand(!expand)}
            >
                {expand ? collapse_label : expand_label}
            </Link>

        );

    const retVal = (
        <div>
            {expand_btn}
            {ViewJSON(data, indent_width, expand)}
        </div>
    );
    return (
        <FunctionField render={() => retVal}/>
    );
}

export default JsonField;
