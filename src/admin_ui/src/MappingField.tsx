import * as React from 'react';
import {Children, cloneElement, FunctionComponent, isValidElement, ReactElement} from 'react';
import {Record} from 'ra-core';
import FormLabel from '@material-ui/core/FormLabel';
import FormControl from '@material-ui/core/FormControl';


export interface MappingFieldProps {
    source: string;
    children: ReactElement | [ReactElement];
    label?: string | ReactElement;
    basePath?: string;
    record?: Record;
    resource?: string;
    variant?: string;
    margin?: "none" | "dense" | "normal";
}

export const MappingField: FunctionComponent<MappingFieldProps> =
    ({
         label,
         children,
         record,
         resource,
         source,
         basePath,
     }) => {
        return (
            <FormControl component="fieldset">
                <FormLabel component="legend">{label}</FormLabel>
                {
                    Children.map(
                        children,
                        (field, field_index?: number) => {
                            if (!isValidElement(field)) {
                                return null;
                            }
                            let field_source = source;
                            if (field.props.source) {
                                field_source = `${source}.${field.props.source}`;
                            }
                            if (field.props.source) {
                                field_index = undefined;
                            }
                            return (
                                <>
                                    {cloneElement(field, {
                                        source: field_source,
                                        index: field_index,
                                        record: record,
                                        resource: resource,
                                        basePath: field.props.basePath || basePath,
                                    })}
                                </>
                            );
                        }
                    )
                }
            </FormControl>
        );
    }

export default MappingField;
