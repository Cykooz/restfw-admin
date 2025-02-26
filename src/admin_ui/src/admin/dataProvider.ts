import queryString from 'query-string';
import {DataProvider, fetchUtils, UpdateParams} from 'ra-core';
import {IApiInfo} from "./apiInfo";
import {IHttpClient} from "./types";
import {HttpError} from "react-admin";
import {IFile, IFileUploadProvider} from "./uploadProvider";
import {
    CreateParams,
    CreateResult,
    DeleteManyParams,
    DeleteManyResult,
    DeleteParams,
    DeleteResult,
    GetListParams,
    GetListResult,
    GetManyParams,
    GetManyReferenceParams,
    GetManyReferenceResult,
    GetManyResult,
    Identifier,
    QueryFunctionContext,
    RaRecord,
    UpdateManyParams,
    UpdateManyResult,
    UpdateResult
} from "ra-core/dist/cjs/types";
import {GetOneParams, GetOneResult} from "ra-core/src/types";

/**
 * Maps react-admin queries to a HAL REST API
 *
 * @example
 *
 * getList          => GET http://my.api.url/posts?_sort=title&_order=ASC&_start=0&_end=24
 * getOne           => GET http://my.api.url/posts/123
 * getManyReference => GET http://my.api.url/posts?author_id=345
 * getMany          => GET http://my.api.url/posts/123, GET http://my.api.url/posts/456, GET http://my.api.url/posts/789
 * create           => POST http://my.api.url/posts/123
 * update           => PUT http://my.api.url/posts/123
 * updateMany       => PUT http://my.api.url/posts/123, PUT http://my.api.url/posts/456, PUT http://my.api.url/posts/789
 * delete           => DELETE http://my.api.url/posts/123
 *
 * @example
 *
 * import React from 'react';
 * import { Admin, Resource } from 'react-admin';
 * import jsonServerProvider from 'ra-data-json-server';
 *
 * import { PostList } from './posts';
 *
 * const App = () => (
 *     <Admin dataProvider={jsonServerProvider('http://jsonplaceholder.typicode.com')}>
 *         <Resource name="posts" list={PostList} />
 *     </Admin>
 * );
 *
 * export default App;
 */

class DefaultDataProvider implements DataProvider {
    apiInfo: IApiInfo;
    uploadProvider: IFileUploadProvider;
    httpClient: IHttpClient;
    supportAbortSignal?: boolean | undefined;
    [key: string]: any;

    constructor(
        apiInfo: IApiInfo,
        uploadProvider: IFileUploadProvider,
        httpClient: IHttpClient = fetchUtils.fetchJson,
    ) {
        this.apiInfo = apiInfo;
        this.uploadProvider = uploadProvider;
        this.httpClient = httpClient;
    }

    async getList<RecordType extends RaRecord = any>(
        resource: string,
        params: GetListParams & QueryFunctionContext
    ): Promise<GetListResult<RecordType>> {
        let page = 1;
        let perPage = 100;
        if (params.pagination) {
            page = params.pagination.page;
            perPage = params.pagination.perPage;
        }
        const orderBy = this.apiInfo.getOrderBy(resource, params.sort);
        let get_total_count = !this.apiInfo.isInfinitePagination(resource);
        let total_count: number | undefined = undefined;
        let data: any[] = [];
        const offset = (page - 1) * perPage;
        const query = {
            ...params.filter,
            ...orderBy,
            offset: offset,
            limit: perPage,
            total_count: get_total_count
        };
        let page_url: string | null = `${this.apiInfo.resourceUrl(resource)}?${queryString.stringify(query)}`;

        while (page_url && perPage > 0) {
            const {headers, json} = await this.httpClient(page_url);
            if (get_total_count) {
                total_count = getTotalCount(headers);
                get_total_count = false;
            }
            const embedded = this.apiInfo.getEmbeddedResources(resource, json);
            data = data.concat(embedded);
            page_url = this.apiInfo.getLink('next', json);
            perPage -= embedded.length;
        }

        return {
            data: data,
            total: total_count,
            pageInfo: {
                hasNextPage: !!page_url
            }
        };
    }

    async getOne<RecordType extends RaRecord = any>(
        resource: string,
        params: GetOneParams<RecordType> & QueryFunctionContext
    ): Promise<GetOneResult<RecordType>> {
        const url = `${this.apiInfo.resourceUrl(resource)}/${params.id}`;
        const {json} = await this.httpClient(url);

        return {
            data: {
                ...json,
                id: this.apiInfo.resourceId(resource, json, params.id)
            },
        };
    }

    async getMany<RecordType extends RaRecord = any>(
        resource: string,
        params: GetManyParams<RecordType> & QueryFunctionContext
    ): Promise<GetManyResult<RecordType>> {
        let filter: { [key: string]: any } = {};
        if (Object.prototype.hasOwnProperty.call(params, "meta")) {
            const meta = params.meta;
            if (meta && Object.prototype.hasOwnProperty.call(meta, 'filter')) {
                filter = meta.filter;
            }
        }
        const query: { [key: string]: any } = {
            total_count: true,
            ...filter
        };
        if (params.ids.length > 0) {
            const filter_name = this.apiInfo.resourceIdField(resource) + '__in';
            query[filter_name] = params.ids;
        }

        const url = `${this.apiInfo.resourceUrl(resource)}?${queryString.stringify(query)}`;
        const {json} = await this.httpClient(url);

        return {
            data: this.apiInfo.getEmbeddedResources(resource, json),
        };
    }

    async getManyReference<RecordType extends RaRecord = any>(
        resource: string,
        params: GetManyReferenceParams & QueryFunctionContext
    ): Promise<GetManyReferenceResult<RecordType>> {
        const {page, perPage} = params.pagination;
        const orderBy = this.apiInfo.getOrderBy(resource, params.sort);
        const query = {
            ...params.filter,
            ...orderBy,
            offset: (page - 1) * perPage,
            limit: perPage,
            total_count: true
        };

        const url = `${this.apiInfo.resourceUrl(resource)}?${queryString.stringify(query)}`;
        const {headers, json} = await this.httpClient(url);

        return {
            data: this.apiInfo.getEmbeddedResources(resource, json),
            total: getTotalCount(headers),
        };
    }

    async upload_files(
        resource: string,
        params: CreateParams | UpdateParams | UpdateManyParams
    ): Promise<void> {
        const file_filed_names = this.apiInfo.resourceFileInputs(resource);
        let file_fields: { [name: string]: IFile } = {};
        for (const i in file_filed_names) {
            const name = file_filed_names[i];
            if (name in params.data) {
                file_fields[name] = params.data[name];
            }
        }
        if (file_fields) {
            file_fields = await this.uploadProvider.upload(resource, file_fields);
            for (const i in file_filed_names) {
                const name = file_filed_names[i];
                if (name in file_fields) {
                    params.data[name] = file_fields[name];
                } else if (name in params.data) {
                    delete params.data[name];
                }
            }
        }
    }

    async update<RecordType extends RaRecord = any>(
        resource: string,
        params: UpdateParams
    ): Promise<UpdateResult<RecordType>> {
        const url = `${this.apiInfo.resourceUrl(resource)}/${params.id}`;
        const update_method = this.apiInfo.resourceUpdateMethod(resource);
        await this.upload_files(resource, params);

        const {json} = await this.httpClient(url, {
            method: update_method,
            body: JSON.stringify(params.data),
        }).catch(on_validation_error);

        return {
            data: {
                ...json,
                id: this.apiInfo.resourceId(resource, json, params.id)
            },
        };
    }

    // HAL doesn't handle filters on UPDATE route, so we make a fallback to calling UPDATE n times instead
    async updateMany<RecordType extends RaRecord = any>(
        resource: string,
        params: UpdateManyParams
    ): Promise<UpdateManyResult<RecordType>> {
        const update_method = this.apiInfo.resourceUpdateMethod(resource);
        const url = `${this.apiInfo.resourceUrl(resource)}`;
        await this.upload_files(resource, params);

        const tasks = params.ids.map(async (id) => {
            const {json} = await this.httpClient(`${url}/${id}`, {
                method: update_method,
                body: JSON.stringify(params.data),
            }).catch(on_validation_error);
            return this.apiInfo.resourceId(resource, json, id);
        });
        return {data: await Promise.all(tasks)};
    }


    async create<
        RecordType extends Omit<RaRecord, 'id'> = any,
        ResultRecordType extends RaRecord = RecordType & { id: Identifier; }
    >(
        resource: string,
        params: CreateParams
    ): Promise<CreateResult<ResultRecordType>> {
        const url = `${this.apiInfo.resourceUrl(resource)}`;
        await this.upload_files(resource, params);

        const {json} = await this.httpClient(url, {
            method: 'POST',
            body: JSON.stringify(params.data),
        }).catch(on_validation_error);
        return {
            data: {
                ...json,
                id: this.apiInfo.resourceId(resource, json)
            },
        };
    }

    async delete<RecordType extends RaRecord = any>(
        resource: string,
        params: DeleteParams<RecordType>
    ): Promise<DeleteResult<RecordType>> {
        const url = `${this.apiInfo.resourceUrl(resource)}/${params.id}`;

        const {json} = await this.httpClient(url, {
            method: 'DELETE',
            body: JSON.stringify({}),
        });
        return {data: json};
    }

    // HAL doesn't handle filters on DELETE route,
    // so we make a fallback to calling DELETE n times instead
    async deleteMany<RecordType extends RaRecord = any>(
        resource: string,
        params: DeleteManyParams<RecordType>
    ): Promise<DeleteManyResult<RecordType>> {
        const url = `${this.apiInfo.resourceUrl(resource)}`;

        const tasks = params.ids.map(async (id) => {
            await this.httpClient(`${url}/${id}`, {
                method: 'DELETE',
                body: JSON.stringify({}),
            });
            return id;
        });
        return {data: await Promise.all(tasks)};
    }
}


function getTotalCount(headers: Headers): number {
    let total = headers.get('x-total-count') || '';
    if (!total) {
        throw new Error(
            'The X-Total-Count header is missing or empty in the HTTP Response. ' +
            'The HAL Data Provider expects responses for lists of ' +
            'resources to contain this header with the total number of results ' +
            'to build the pagination. If you are using CORS, did you declare ' +
            'X-Total-Count in the Access-Control-Expose-Headers header?'
        );
    }
    total = total.split('/').pop() || '0';

    return parseInt(total, 10);
}


function on_validation_error(error: HttpError) {
    if (error.status === 422) {
        return Promise.reject(new HttpError(
            error.body.description,
            error.status,
            {
                errors: error.body.detail,
            },
        ));
    }
    return Promise.reject(error)
}

export default function halRestDataProvider(
    apiInfo: IApiInfo,
    uploadProvider: IFileUploadProvider,
    httpClient: IHttpClient = fetchUtils.fetchJson,
): DataProvider {
    return new DefaultDataProvider(apiInfo, uploadProvider, httpClient);
}
