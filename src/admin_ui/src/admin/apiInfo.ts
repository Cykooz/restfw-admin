import {Identifier, RaRecord, SortPayload} from "ra-core";


export interface IValidator {
    name: string;
    args: any[];
}

export interface IField {
    type: string;
    source: string;
    params: any;
    validators: IValidator[];
}

export interface IListView {
    fields: IField[];
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

    getOrderBy(name: string, sort: SortPayload): { [key: string]: string };

    resourceId(name: string, data: any, def?: Identifier | null): Identifier;

    resourceUpdateMethod(name: string): string;

    getEmbeddedResources<RecordType extends RaRecord = RaRecord>(name: string, data: any): RecordType[];

    mapResources<T>(callback: MapCallback<T>): T[];
}


export class ApiInfo implements IApiInfo {
    private readonly root_url: string;
    private readonly title: string;
    private readonly resources: {
        [name: string]: IResourceInfo
    };
    private readonly extra: {
        [name: string]: any
    };

    constructor(public raw_info: any) {
        this.root_url = raw_info.root_url;
        this.title = raw_info.title;
        this.resources = raw_info.resources;
        this.extra = raw_info.extra;
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

    getOrderBy(name: string, sort: SortPayload): { [key: string]: string } {
        if (!(name in this.resources)) {
            console.warn(`ApiInfo: Unknown resource with a name "${name}".`);
            return {};
        }
        const resource = this.resources[name];
        const {field, order} = sort;
        if (field && resource.order_by.includes(field)) {
            const sign = order === 'ASC' ? '' : '-';
            return {
                'order_by': `${sign}${field}`
            };
        }
        return {};
    }

    resourceId(name: string, data: any, def: Identifier | null = null): Identifier {
        if (name in this.resources) {
            const info = this.resources[name];
            if (info.id_field && data.hasOwnProperty(info.id_field))
                return data[info.id_field];
        }

        if (data.hasOwnProperty('id'))
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

        if (!data.hasOwnProperty('_embedded')) {
            console.warn(`ApiInfo: "_embedded" field is absent in data for "${name}" resource.`);
            return [];
        }

        const embedded_name = this.resources[name].embedded_name;
        if (!embedded_name) {
            console.warn(`ApiInfo: Option "embedded_name" for "${name}" resource is empty.`);
            return [];
        }

        const embedded_data = data._embedded;
        if (!embedded_data.hasOwnProperty(embedded_name)) {
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

    mapResources<T>(callback: MapCallback<T>): T[] {
        let result: T[] = [];
        for (let key in this.resources) {
            const resourceInfo = this.resources[key];
            result.push(callback(resourceInfo));
        }
        return result;
    }

    getExtra(): { [name: string]: any } {
        return this.extra;
    }
}

export default ApiInfo;
