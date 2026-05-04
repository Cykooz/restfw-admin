import Chip from '@mui/material/Chip';
import type { ChangeEvent } from 'react';
import InputAdornment from '@mui/material/InputAdornment';
import TextField from '@mui/material/TextField';
import {
    FieldTitle,
    TextInputProps,
    useInput,
    useTranslate,
} from 'react-admin';

export interface NullableTextInputProps extends TextInputProps {
    nullChipLabel?: string;
}

const defaultParse = (value: string) => value;
const defaultFormat = (value: unknown) => value;

/**
 * `NullableTextInput` behaves like react-admin `TextInput`, but preserves the
 * difference between `null` and an empty string.
 *
 * The "Null" chip shows whether the current value is `null`.
 * Clicking the chip toggles the value between `null` and `''`.
 */
export const NullableTextInput = (props: NullableTextInputProps) => {
    const {
        source,
        label,
        helperText,
        disabled,
        readOnly,
        nullChipLabel = 'Null',
        variant = 'filled',
        margin = 'dense',
        fullWidth = true,
        slotProps,
        parse = defaultParse,
        format = defaultFormat,
        onBlur,
        onChange,
        validate,
        defaultValue,
        ...rest
    } = props;

    const translate = useTranslate();

    const {
        field,
        fieldState: { error, invalid },
        id,
        isRequired,
    } = useInput({
        source,
        disabled,
        readOnly,
        parse,
        format,
        onBlur,
        onChange,
        validate,
        defaultValue,
        ...rest,
    });

    const isNull = field.value === null;
    const inputSlotProps =
        typeof slotProps?.input === 'function' ? {} : slotProps?.input;
    const htmlInputSlotProps =
        typeof slotProps?.htmlInput === 'function' ? {} : slotProps?.htmlInput;

    const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
        field.onChange(event.target.value);
    };

    const handleToggleNull = () => {
        if (disabled || readOnly) {
            return;
        }

        field.onChange(isNull ? '' : null);
    };

    const renderHelperText = () => {
        if (invalid && error?.message) {
            return translate(error.message, {
                _: error.message,
            });
        }

        return helperText;
    };

    return (
        <TextField
            {...rest}
            id={id}
            name={field.name}
            label={
                label !== false ? (
                    <FieldTitle
                        label={label}
                        source={source}
                        isRequired={isRequired}
                    />
                ) : undefined
            }
            value={isNull ? '' : (field.value ?? '')}
            onChange={handleChange}
            onBlur={field.onBlur}
            inputRef={field.ref}
            disabled={disabled}
            slotProps={{
                ...slotProps,
                input: {
                    ...inputSlotProps,
                    readOnly,
                    endAdornment: (
                        <>
                            {inputSlotProps?.endAdornment}
                            <InputAdornment position="end">
                                <Chip
                                    label={nullChipLabel}
                                    size="small"
                                    color={isNull ? 'primary' : 'default'}
                                    variant={isNull ? 'filled' : 'outlined'}
                                    onClick={handleToggleNull}
                                    clickable={!disabled && !readOnly}
                                    aria-pressed={isNull}
                                    // sx={{
                                    //     fontWeight: isNull ? 700 : 400,
                                    //     opacity: disabled ? 0.5 : 1,
                                    //     borderWidth: 1,
                                    //     borderStyle: isNull ? 'solid' : 'dashed',
                                    //     borderColor: isNull
                                    //         ? 'primary.main'
                                    //         : 'text.disabled',
                                    //     backgroundColor: isNull
                                    //         ? 'primary.main'
                                    //         : 'transparent',
                                    //     color: isNull
                                    //         ? 'primary.contrastText'
                                    //         : 'text.secondary',
                                    //     '&:hover': {
                                    //         backgroundColor: isNull
                                    //             ? 'primary.dark'
                                    //             : 'action.hover',
                                    //     },
                                    // }}
                                />
                            </InputAdornment>
                        </>
                    ),
                },
                htmlInput: htmlInputSlotProps,
            }}
            error={invalid}
            helperText={renderHelperText()}
            variant={variant}
            margin={margin}
            fullWidth={fullWidth}
        />
    );
};
