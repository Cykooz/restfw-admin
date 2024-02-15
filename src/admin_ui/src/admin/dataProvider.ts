import {stringify} from 'query-string';
import {DataProvider, fetchUtils} from 'ra-core';
import {IApiInfo} from "./apiInfo";
import {IHttpClient} from "./types";
import {HttpError} from "react-admin";

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
const Provider = (apiInfo: IApiInfo, httpClient: IHttpClient = fetchUtils.fetchJson): DataProvider => ({
    getList: async (resource, params) => {
        let {page, perPage} = params.pagination;
        const orderBy = apiInfo.getOrderBy(resource, params.sort);
        let get_total_count = true;
        let total_count = 0;
        let data: any[] = [];
        let offset = (page - 1) * perPage;

        while (perPage > 0) {
            const query = {
                ...params.filter,
                ...orderBy,
                offset: offset,
                limit: perPage,
                total_count: get_total_count
            };

            const url = `${apiInfo.resourceUrl(resource)}?${stringify(query)}`;
            const {headers, json} = await httpClient(url);

            if (get_total_count) {
                total_count = getTotalCount(headers);
                get_total_count = false;
            }
            const embedded = apiInfo.getEmbeddedResources(resource, json);
            data = data.concat(embedded);
            if (embedded.length < perPage) {
                break;
            }
            offset += embedded.length;
            if (offset >= total_count) {
                break;
            }
            perPage -= embedded.length;
        }

        return {
            data: data,
            total: total_count,
        };
    },

    getOne: async (resource, params) => {
        const url = `${apiInfo.resourceUrl(resource)}/${params.id}`;
        const {json} = await httpClient(url);

        return {
            data: {
                ...json,
                id: apiInfo.resourceId(resource, json, params.id)
            },
        };
    },

    getMany: async (resource, params) => {
        let filter: { [key: string]: any } = {};
        if (params.hasOwnProperty("meta")) {
            let meta = params.meta;
            if (meta && meta.hasOwnProperty('filter')) {
                filter = meta.filter;
            }
        }
        let query: { [key: string]: any } = {
            total_count: true,
            ...filter
        };
        if (params.ids.length > 0) {
            const filter_name = apiInfo.resourceIdField(resource) + '__in';
            query[filter_name] = params.ids;
        }

        const url = `${apiInfo.resourceUrl(resource)}?${stringify(query)}`;
        const {json} = await httpClient(url);

        return {
            data: apiInfo.getEmbeddedResources(resource, json),
        };
    },

    getManyReference: async (resource, params) => {
        const {page, perPage} = params.pagination;
        const orderBy = apiInfo.getOrderBy(resource, params.sort);
        const query = {
            ...params.filter,
            ...orderBy,
            offset: (page - 1) * perPage,
            limit: perPage,
            total_count: true
        };

        const url = `${apiInfo.resourceUrl(resource)}?${stringify(query)}`;
        const {headers, json} = await httpClient(url);

        return {
            data: apiInfo.getEmbeddedResources(resource, json),
            total: getTotalCount(headers),
        };
    },

    update: async (resource, params) => {
        const url = `${apiInfo.resourceUrl(resource)}/${params.id}`;
        const update_method = apiInfo.resourceUpdateMethod(resource);

        const {json} = await httpClient(url, {
            method: update_method,
            body: JSON.stringify(params.data),
        }).catch(on_validation_error);

        return {
            data: {
                ...json,
                id: apiInfo.resourceId(resource, json, params.id)
            },
        };
    },

    // HAL doesn't handle filters on UPDATE route, so we make a fallback to calling UPDATE n times instead
    updateMany: async (resource, params) => {
        const update_method = apiInfo.resourceUpdateMethod(resource);
        const url = `${apiInfo.resourceUrl(resource)}`;

        const tasks = params.ids.map(async (id) => {
            const {json} = await httpClient(`${url}/${id}`, {
                method: update_method,
                body: JSON.stringify(params.data),
            }).catch(on_validation_error);
            return apiInfo.resourceId(resource, json, id);
        });
        return {data: await Promise.all(tasks)};
    },

    create: async (resource, params) => {
        const url = `${apiInfo.resourceUrl(resource)}`;

        const {json} = await httpClient(url, {
            method: 'POST',
            body: JSON.stringify(params.data),
        }).catch(on_validation_error);
        return {
            data: {
                ...json,
                id: apiInfo.resourceId(resource, json)
            },
        };
    },

    delete: async (resource, params) => {
        const url = `${apiInfo.resourceUrl(resource)}/${params.id}`;

        const {json} = await httpClient(url, {
            method: 'DELETE',
            body: JSON.stringify({}),
        });
        return {data: json};
    },

    // HAL doesn't handle filters on DELETE route,
    // so we make a fallback to calling DELETE n times instead
    deleteMany: async (resource, params) => {
        const url = `${apiInfo.resourceUrl(resource)}`;

        const tasks = params.ids.map(async (id) => {
            await httpClient(`${url}/${id}`, {
                method: 'DELETE',
                body: JSON.stringify({}),
            });
            return id;
        });
        return {data: await Promise.all(tasks)};
    },
});


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

export default Provider;
