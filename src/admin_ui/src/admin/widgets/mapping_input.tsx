import {Children, cloneElement, FC, ReactElement} from 'react';
import {InputProps} from 'ra-core';
import FormLabel from '@mui/material/FormLabel';
import FormControl from '@mui/material/FormControl';


export interface MappingInputProps extends InputProps {
    children: ReactElement<InputProps> | ReactElement<InputProps>[];
}


export const MappingInput: FC<MappingInputProps> =
    ({
         label,
         children,
         source,
     }) => {
        return (
            <FormControl component="fieldset"
                         sx={{
                             paddingLeft: '12px',
                             paddingRight: '12px',
                             border: (theme) => `1px solid ${theme.palette.grey[500]}`
                         }}
            >
                <FormLabel component="legend" sx={{paddingLeft: '5px', paddingRight: '5px'}}>
                    {label}
                </FormLabel>
                {
                    Children.map(
                        children,
                        (field, field_index?: number) => {
                            let field_source = source;
                            if (field.props.source) {
                                field_source = `${source}.${field.props.source}`;
                            }
                            // if (field.props.source) {
                            //     field_index = undefined;
                            // }
                            return cloneElement(field, {
                                source: field_source,
                                // index: field_index,
                            });
                        }
                    )
                }
            </FormControl>
        );
    }

export default MappingInput;
