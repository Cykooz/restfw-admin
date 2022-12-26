import * as React from 'react';
import {Children, cloneElement, FunctionComponent, ReactElement} from 'react';
import FormControl from '@mui/material/FormControl';
import {Labeled} from 'react-admin';
import {InjectedFieldProps, PublicFieldProps} from "ra-ui-materialui/src/field/types";

export interface MappingFieldProps
    extends PublicFieldProps,
        InjectedFieldProps {
    children: ReactElement | ReactElement[];
}

export const MappingField: FunctionComponent<MappingFieldProps> =
    ({
         children,
         source,
     }) => {
        return (
            <FormControl component="fieldset" sx={{paddingLeft: '12px'}}>
                {
                    Children.map(
                        children,
                        (field, field_index?: number) => {
                            // if (!isValidElement(field)) {
                            //     return null;
                            // }
                            let field_source = source;
                            if (field.props.source) {
                                field_source = `${source}.${field.props.source}`;
                            }
                            if (field.props.source) {
                                field_index = undefined;
                            }
                            return (
                                <Labeled label={field.props.label}>
                                    {cloneElement(field, {
                                        source: field_source,
                                        index: field_index,
                                    })}
                                </Labeled>
                            );
                        }
                    )
                }
            </FormControl>
        );
    }

export default MappingField;
