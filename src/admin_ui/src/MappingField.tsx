import * as React from 'react';
import {Children, cloneElement, FunctionComponent, isValidElement, ReactElement} from 'react';
import {Record} from 'ra-core';
import FormLabel from '@material-ui/core/FormLabel';
import FormControl from '@material-ui/core/FormControl';
import {Labeled} from 'react-admin';
import {makeStyles} from '@material-ui/core/styles';
import {Theme} from '@material-ui/core/styles/createMuiTheme';


const useStyles = makeStyles((theme: Theme) => ({
  fieldset: {
      padding: '5px 12px',
      border: `1px solid ${theme.palette.grey[500]}`,
  },
  legend: {
      paddingLeft: '5px',
      paddingRight: '5px',
      fontSize: theme.typography.pxToRem(12),
  },
}));

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
        const classes = useStyles();
        return (
            <FormControl component="fieldset" className={classes.fieldset}>
                <FormLabel component="legend" className={classes.legend}>{label}</FormLabel>
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
                                <Labeled label={field.props.label}>
                                    {cloneElement(field, {
                                        source: field_source,
                                        index: field_index,
                                        record: record,
                                        resource: resource,
                                        basePath: field.props.basePath || basePath,
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
