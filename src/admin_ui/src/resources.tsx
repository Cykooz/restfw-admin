import React from "react";
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
import {makeStyles} from '@material-ui/core';


export function getResources(apiInfo: IApiInfo) {
    return (
        apiInfo.mapResources((resourceInfo) => (
            <Resource
                key={resourceInfo.name}
                name={resourceInfo.name}
                {...getResourceViews(resourceInfo)}
            />
        ))
    );
}


function getResourceViews(resourceInfo: IResourceInfo) {
    return {
        list: getListView(resourceInfo),
        show: getShowView(resourceInfo),
        create: getCreateView(resourceInfo),
        edit: getEditView(resourceInfo),
    };
}


const useGridStyles = makeStyles({
    headerCell: {
        backgroundColor: '#e0e0e0',
    },
});


function getListView(resourceInfo: IResourceInfo) {
    const {list, show, edit} = resourceInfo.views;
    if (!list) {
        return null;
    }
    return (props: any) => {
        if (!resourceInfo.deletable)
            props['bulkActionButtons'] = false;
        const classes = useGridStyles();
        return (
            <List {...props}>
                <Datagrid rowClick={show ? 'show' : ''} classes={classes}>
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

    return (props: any) => {
        return (
            <Show {...props}>
                <SimpleShowLayout>
                    {getFields(show.fields)}
                </SimpleShowLayout>
            </Show>
        );
    };
}


function getCreateView(resourceInfo: IResourceInfo) {
    const {create} = resourceInfo.views;
    if (!create) {
        return null;
    }

    return (props: any) => {
        return (
            <Create {...props}>
                <SimpleForm>
                    {getInputs(create.fields)}
                </SimpleForm>
            </Create>
        );
    };
}


const EditWithoutDeleteToolbar = props => (
    <Toolbar {...props} >
        <SaveButton/>
    </Toolbar>
);


function getEditView(resourceInfo: IResourceInfo) {
    const {edit} = resourceInfo.views;
    if (!edit) {
        return null;
    }
    let form_props = {};
    if (!resourceInfo.deletable) {
        form_props['toolbar'] = <EditWithoutDeleteToolbar/>;
    }

    return (props: any) => {
        return (
            <Edit {...props}>
                <SimpleForm {...form_props}>
                    {getInputs(edit.fields)}
                </SimpleForm>
            </Edit>
        );
    };
}
