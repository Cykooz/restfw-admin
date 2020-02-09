import React from "react";
import {Create, Datagrid, Edit, EditButton, List, Resource, Show, SimpleForm, SimpleShowLayout} from "react-admin";
import {IApiInfo, IResourceInfo} from "./apiInfo";
import {getFields, getInputs} from "./fields";


export function getResources(apiInfo: IApiInfo) {
    return (
        apiInfo.mapResources((resourceInfo) => (
            <Resource
                key={resourceInfo.index}
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


function getListView(resourceInfo: IResourceInfo) {
    const {list, show, edit} = resourceInfo.views;
    if (!list) {
        return null;
    }

    return (props: any) => {
        return (
            <List {...props}>
                <Datagrid rowClick={show ? 'show' : ''}>
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


function getEditView(resourceInfo: IResourceInfo) {
    const {edit} = resourceInfo.views;
    if (!edit) {
        return null;
    }

    return (props: any) => {
        return (
            <Edit {...props}>
                <SimpleForm>
                    {getInputs(edit.fields)}
                </SimpleForm>
            </Edit>
        );
    };
}
