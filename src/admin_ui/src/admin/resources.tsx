import React, {ReactElement} from "react";
import {
    Create,
    Datagrid,
    Edit,
    EditButton,
    List,
    Resource,
    SaveButton,
    Show,
    SimpleForm,
    SimpleShowLayout,
    Toolbar
} from "react-admin";
import {IApiInfo, IResourceInfo} from "./apiInfo";
import {getFields, getInputs} from "./fields";


export function getResources(apiInfo: IApiInfo) {
    return (
        apiInfo.mapResources((resourceInfo) => (
            <Resource
                key={resourceInfo.name}
                name={resourceInfo.name}
                options={{label: resourceInfo.title}}
                {...getResourceViews(resourceInfo)}
            />
        ))
    );
}


function getResourceViews(resourceInfo: IResourceInfo) {
    const list = getListView(resourceInfo);
    const show = getShowView(resourceInfo);
    const create = getCreateView(resourceInfo);
    const edit = getEditView(resourceInfo);
    return Object.assign({},
        list === null ? null : {list},
        show === null ? null : {show},
        create === null ? null : {create},
        edit === null ? null : {edit},
    );
    // return {
    //     list: getListView(resourceInfo),
    //     show: getShowView(resourceInfo),
    //     create: getCreateView(resourceInfo),
    //     edit: getEditView(resourceInfo),
    // };
}

class GridProps {
    bulkActionButtons?: ReactElement | false;
}

function getListView(resourceInfo: IResourceInfo) {
    const {list, show, edit} = resourceInfo.views;
    if (!list) {
        return null;
    }
    return () => {
        let grid_props = new GridProps();
        if (!resourceInfo.deletable)
            grid_props.bulkActionButtons = false;
        let filters = getInputs(list.filters || []);
        return (
            <List filters={filters}>
                <Datagrid
                    rowClick={show ? 'show' : ''}
                    sx={{
                        '& .RaDatagrid-headerCell': {
                            backgroundColor: '#e0e0e0',
                        },
                    }}
                    {...grid_props}
                >
                    {getFields(list.fields)}
                    {edit ? <EditButton/> : null}
                </Datagrid>
            </List>
        );
    };
}

function getShowView(resourceInfo: IResourceInfo) {
    const {show} = resourceInfo.views;
    if (!show) {
        return null;
    }
    return () => {
        return (
            <Show>
                <SimpleShowLayout>
                    {getFields(show.fields)}
                </SimpleShowLayout>
            </Show>
        );
    };
}


const CreateToolbar = (props: any) => (
    <Toolbar {...props} >
        <SaveButton alwaysEnable/>
    </Toolbar>
);


function getCreateView(resourceInfo: IResourceInfo) {
    const {create} = resourceInfo.views;
    if (!create) {
        return null;
    }

    return () => {
        return (
            <Create>
                <SimpleForm toolbar={<CreateToolbar/>}>
                    {getInputs(create.fields)}
                </SimpleForm>
            </Create>
        );
    };
}


const EditWithoutDeleteToolbar = () => (
    <Toolbar>
        <SaveButton />
    </Toolbar>
);


class FormProps {
    toolbar?: ReactElement | false;
}

function getEditView(resourceInfo: IResourceInfo) {
    const {edit} = resourceInfo.views;
    if (!edit) {
        return null;
    }
    let form_props = new FormProps();
    if (!resourceInfo.deletable) {
        form_props.toolbar = <EditWithoutDeleteToolbar/>;
    }

    return () => {
        return (
            <Edit mutationMode="pessimistic">
                <SimpleForm {...form_props}>
                    {getInputs(edit.fields)}
                </SimpleForm>
            </Edit>
        );
    };
}
