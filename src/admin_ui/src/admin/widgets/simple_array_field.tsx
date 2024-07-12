import {useRecordContext} from "react-admin";
import Chip from '@mui/material/Chip'
import {ReactElement} from "react";


export interface SimpleArrayFieldProps {
    source: string;
    break_lines?: boolean;
}

export const SimpleArrayField = (props: SimpleArrayFieldProps) => {
    const {
        source,
        break_lines = false,
    } = props;
    const record = useRecordContext();
    if (!record) {
        return <div/>
    }
    const array = record[source]
    if (typeof array === 'undefined' || array === null || array.length === 0) {
        return <div/>
    } else {
        const elements: ReactElement[] = [];
        array.forEach((item: any, index: number) => {
                elements.push(<Chip label={item} key={item}/>);
                if (break_lines && index < array.length - 1) {
                    elements.push(<br/>)
                }
            }
        );
        return <>{elements}</>
    }
}

export default SimpleArrayField;

