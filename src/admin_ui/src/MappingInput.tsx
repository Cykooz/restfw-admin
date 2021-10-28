import * as React from 'react';
import {Children, cloneElement, FC, isValidElement, ReactElement} from 'react';
import {InputProps, Record} from 'ra-core';
import FormLabel from '@material-ui/core/FormLabel';
import FormControl from '@material-ui/core/FormControl';
import {makeStyles} from '@material-ui/core/styles';
import {Theme} from '@material-ui/core';

const useStyles = makeStyles((theme: Theme) => ({
    fieldset: {
        padding: '5px 12px',
        border: `1px solid ${theme.palette.grey[500]}`,
    },
    legend: {
        paddingLeft: '5px',
        paddingRight: '5px',
    },
}));


export interface MappingInputProps extends InputProps {
    children: ReactElement | ReactElement[];
    label?: string | ReactElement;
    basePath?: string;
    record: Record;
    resource: string;
    // variant?: string;
    // margin?: "none" | "dense" | "normal";
}


export const MappingInput: FC<MappingInputProps> =
    ({
         label,
         children,
         record,
         resource,
         source,
         // variant,
         basePath,
         // margin = 'dense',
     }) => {
        const classes = useStyles();
        return (
            <FormControl component="fieldset" className={classes.fieldset}>
                <FormLabel component="legend" className={classes.legend}>{label}</FormLabel>
                {
                    Children.map(
                        children,
                        (input, input_index?: number) => {
                            if (!isValidElement(input)) {
                                return null;
                            }
                            let input_source = source;
                            if (input.props.source) {
                                input_source = `${source}.${input.props.source}`;
                            }
                            if (input.props.source) {
                                input_index = undefined;
                            }
                            return cloneElement(input, {
                                source: input_source,
                                index: input_index,
                                record: record,
                                resource: resource,
                                basePath: input.props.basePath || basePath,
                            });

                            // return (
                            //     <FormInput
                            //         basePath={
                            //             input.props.basePath || basePath
                            //         }
                            //         input={cloneElement(input, {
                            //             source: input_source,
                            //             index: input_index,
                            //         })}
                            //         record={record}
                            //         resource={resource}
                            //         // variant={input.props.variant || variant}
                            //         // margin={input.props.margin || margin}
                            //     />
                            // );
                        }
                    )
                }
            </FormControl>
        );
    }

export default MappingInput;
