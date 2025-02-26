import {Identifier, RaRecord, SortPayload} from "ra-core";
import get from "lodash/get";


export interface IValidator {
    name: string;
    args: any[];
}

export interface IField {
    id: string | null,
    type: string;
    source: string;
    params: any;
    validators: IValidator[];
}

export interface IListView {
    fields: IField[];
    filters: IField[] | null;
    infinite_pagination: boolean;
}

export interface IShowView {
    fields: IField[];
}

export interface ICreateView {
    fields: IField[];
}

export interface IEditView {
    fields: IField[];
}

export interface IResourceInfo {
    index: number;
    name: string;
    title: string;
    location: string;
    id_field: string;
    embedded_name: string;
    update_method: string;
    deletable: boolean;
    order_by: string[];
    extra: {[key: string]: null | string | number | boolean | object};
    views: {
        list: IListView | null,
        show: IShowView | null,
        create: ICreateView | null,
        edit: IEditView | null,
    }
}

type MapCallback<T> = (resource: IResourceInfo) => T;


export interface IApiInfo {
    getTitle(): string;

    rootUrl(): string;

    resourceUrl(name: string): string;

    resourceIdField(name: string): string;

    resourceFileInputs(name: string): string[];

    resourceExtra(name: string): { [key: string]: null | string | number | boolean | object };

    getOrderBy(name: string, sort?: SortPayload): { [key: string]: string };

    resourceId(name: string, data: any, def?: Identifier | null): Identifier;

    resourceUpdateMethod(name: string): string;

    getEmbeddedResources<RecordType extends RaRecord = RaRecord>(name: string, data: any): RecordType[];

    getLink(name: string, data: any): string | null;

    isInfinitePagination(resource_name: string): boolean;

    mapResources<T>(callback: MapCallback<T>): T[];

    getExtra(): { [name: string]: null | string | number | boolean | object };
}


export class ApiInfo implements IApiInfo {
    private readonly root_url: string;
    private readonly title: string;
    private readonly resources: {
        [name: string]: IResourceInfo
    };
    private readonly extra: {
        [name: string]: null | string | number | boolean | object
    };
    private readonly file_inputs: {
        [name: string]: string[]
    };

    constructor(public raw_info: any) {
        this.root_url = raw_info.root_url;
        this.title = raw_info.title;
        this.resources = raw_info.resources;
        this.extra = raw_info.extra;

        const file_inputs: {[name: string]: string[]} = {};
        for (const res_name in this.resources) {
            const info = this.resources[res_name];
            let names: string[] = [];
            if (info.views.create != null) {
                names = names.concat(getFileInputNames(info.views.create.fields, ""));
            }
            if (info.views.edit != null) {
                names = names.concat(getFileInputNames(info.views.edit.fields, ""));
            }
            file_inputs[res_name] = Array.from(new Set(names));
        }
        this.file_inputs = file_inputs;
    }

    getTitle() {
        return this.title;
    }

    rootUrl(): string {
        return this.root_url;
    }

    resourceUrl(name: string) {
        return this.root_url + this.resources[name].location;
    }

    resourceIdField(name: string): string {
        return this.resources[name].id_field;
    }

    resourceFileInputs(name: string): string[] {
        return this.file_inputs[name]
    }

    resourceExtra(name: string): { [key: string]: null | string | number | boolean | object } {
        return this.resources[name].extra;
    }

    getOrderBy(name: string, sort?: SortPayload): { [key: string]: string } {
        if (!(name in this.resources)) {
            console.warn(`ApiInfo: Unknown resource with a name "${name}".`);
            return {};
        }
        const resource = this.resources[name];
        if (sort) {
            const {field, order} = sort;
            if (field && resource.order_by.includes(field)) {
                const sign = order === 'ASC' ? '' : '-';
                return {
                    'order_by': `${sign}${field}`
                };
            }
        }
        return {};
    }

    resourceId(name: string, data: any, def: Identifier | null = null): Identifier {
        if (name in this.resources) {
            const info = this.resources[name];
            if (info.id_field && Object.prototype.hasOwnProperty.call(data, info.id_field))
                return data[info.id_field];
        }

        if (Object.prototype.hasOwnProperty.call(data, 'id'))
            return data.id;

        const self_url = data._links.self.href.split('/');
        const id = self_url[self_url.length - 2];
        if (id)
            return id;
        if (def)
            return def;

        throw Error(`Could not found "id" of "${name}" resource`);
    }

    resourceUpdateMethod(name: string): string {
        if (!(name in this.resources)) {
            console.warn(`ApiInfo: Unknown resource with a name "${name}".`);
            return 'PUT';
        }
        return this.resources[name].update_method;
    }

    getEmbeddedResources<RecordType extends RaRecord = RaRecord>(name: string, data: any): RecordType[] {
        if (!(name in this.resources)) {
            console.warn(`ApiInfo: Unknown resource with a name "${name}".`);
            return [];
        }

        if (!Object.prototype.hasOwnProperty.call(data, '_embedded')) {
            console.warn(`ApiInfo: "_embedded" field is absent in data for "${name}" resource.`);
            return [];
        }

        const embedded_name = this.resources[name].embedded_name;
        if (!embedded_name) {
            console.warn(`ApiInfo: Option "embedded_name" for "${name}" resource is empty.`);
            return [];
        }

        const embedded_data = data._embedded;
        if (!Object.prototype.hasOwnProperty.call(embedded_data, embedded_name)) {
            console.warn(
                `ApiInfo: Embedded resources with a name "${embedded_name}" ` +
                `has not found inside of "_embedded" field of "${name}" resource.`
            );
            return [];
        }

        const embedded_resources: any[] = embedded_data[embedded_name];

        return embedded_resources.map(
            resource_data => ({
                ...resource_data,
                id: this.resourceId(embedded_name, resource_data)
            })
        )
    }

    getLink(name: string, data: any): string | null {
        return get(data, `_links.${name}.href`);
    }

    isInfinitePagination(resource_name: string): boolean {
        if (!(resource_name in this.resources)) {
            console.warn(`ApiInfo: Unknown resource with a name "${resource_name}".`);
            return false;
        }
        const list_view = this.resources[resource_name].views.list;
        if (list_view) {
            return list_view.infinite_pagination;
        }
        return false;
    }

    mapResources<T>(callback: MapCallback<T>): T[] {
        const result: T[] = [];
        for (const key in this.resources) {
            const resourceInfo = this.resources[key];
            result.push(callback(resourceInfo));
        }
        return result;
    }

    getExtra(): { [name: string]: null | string | number | boolean | object } {
        return this.extra;
    }
}


function getFileInputNames(fields_array: IField[], prefix: string): string[] {
    let names: string[] = [];
    for (const i in fields_array) {
        const field = fields_array[i];
        const field_name = prefix.concat(field.source);
        if (field.type == 'FileInput') {
            names.push(field_name);
        } else if (field.type == 'MappingInput' || field.type == 'ArrayInput') {
            const {fields} = field.params;
            if (fields instanceof Array) {
                names = names.concat(getFileInputNames(fields, field_name.concat(".")));
            }
        }
    }
    return names;
}
