/* eslint-disable @typescript-eslint/no-empty-function */
import {FC, memo, ReactElement, useEffect, useState} from 'react';
import get from 'lodash/get';
import {ListContextProvider, useListController, useRecordContext} from 'ra-core';
import {FieldProps} from "react-admin";

export interface NestedArrayFieldProps extends FieldProps {
    children: ReactElement;
}

const initialState: any[] = [];


export const NestedArrayField: FC<NestedArrayFieldProps> = memo(props => {
    const {children, resource, source} = props;
    const record = useRecordContext(props);
    const [data, setData] = useState(initialState);

    useEffect(() => {
        if (record) {
            const data = get_nested_list(record, source || "");
            setData(data);
        }
    }, [record, source]);

    const controllerProps = useListController({
        sort: {field: '', order: 'ASC'},
        perPage: 1000000,
        resource: resource || "",
    });
    controllerProps.data = data;
    controllerProps.total = data.length;
    controllerProps.hasPreviousPage = false;
    controllerProps.hasNextPage = false;
    return (
        <ListContextProvider value={controllerProps}>
            {children}
        </ListContextProvider>
    );
});


function get_nested_list(record: Record<string, any>, path: string | string[]): any[] {
    if (!Array.isArray(path)) {
        path = path.split('.');
    }
    if (path.length === 0) {
        return [record];
    }
    const root_name = path[0];
    const child_path = path.slice(1)
    let child = get(record, root_name)
    let result: any[] = []
    if (Array.isArray(child)) {
        for (const index in child) {
            let child_record = child[index];
            if (child_path.length > 0) {
                if (is_object(child_record)) {
                    result = result.concat(
                        get_nested_list(child_record, child_path)
                    );
                }
            } else {
                if (!is_object(child_record)) {
                    child_record = {_value: child_record};
                }
                result.push(child_record);
            }
        }
    } else if (is_object(child) && child_path.length > 0) {
        result = result.concat(
            get_nested_list(child, child_path)
        )
    } else if (child_path.length === 0) {
        if (!is_object(child)) {
            child = {_value: child};
        }
        result.push(child);
    }
    return result;
}

function is_object(v: any): boolean {
    return (
        typeof v === 'object' &&
        !Array.isArray(v) &&
        v !== null
    )
}


NestedArrayField.displayName = 'NestedArrayField'
