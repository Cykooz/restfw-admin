import Chip from '@mui/material/Chip';
import get from 'lodash/get';
import {
    TextField,
    TextFieldProps,
    useRecordContext,
} from 'react-admin';

export interface NullableTextFieldProps extends TextFieldProps {
    nullChipLabel?: string;
}

/**
 * `NullableTextField` behaves like react-admin `TextField`, but preserves the
 * difference between `null` and an empty string.
 *
 * When the field value is `null`, it renders a "Null" chip instead of the
 * default `TextField` content.
 */
export const NullableTextField = (props: NullableTextFieldProps) => {
    const {
        source,
        nullChipLabel = 'Null',
        ...rest
    } = props;

    const record = useRecordContext(props);

    if (!record || !source) {
        return <TextField source={source} {...rest} />;
    }

    const value = get(record, source);

    if (value === null) {
        return (
            <Chip
                label={nullChipLabel}
                size="small"
            />
        );
    }

    return <TextField source={source} {...rest} />;
};

export default NullableTextField;