import {stringify} from 'query-string';
import {fetchUtils, DataProvider, Sort} from 'ra-core';
import {IApiInfo} from "./apiInfo";

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
export default (apiInfo: IApiInfo, httpClient = fetchUtils.fetchJson): DataProvider => ({
    getList: async (resource, params) => {
        const {page, perPage} = params.pagination;
        const orderBy = sort2orderBy(params.sort);
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
        const query = {
            id: params.ids,
            total_count: true,
        };
        const url = `${apiInfo.resourceUrl(resource)}?${stringify(query)}`;
        const {json} = await httpClient(url);

        return {
            data: apiInfo.getEmbeddedResources(resource, json),
        };
    },

    getManyReference: async (resource, params) => {
        const {page, perPage} = params.pagination;
        const orderBy = sort2orderBy(params.sort);
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
        });

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
            });
            return apiInfo.resourceId(resource, json, id);
        });
        return {data: await Promise.all(tasks)};
    },

    create: async (resource, params) => {
        const url = `${apiInfo.resourceUrl(resource)}`;

        const {json} = await httpClient(url, {
            method: 'POST',
            body: JSON.stringify(params.data),
        });
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
        });
        return {data: json};
    },

    // json-server doesn't handle filters on DELETE route, so we make a fallback to calling DELETE n times instead
    deleteMany: async (resource, params) => {
        const url = `${apiInfo.resourceUrl(resource)}`;

        const tasks = params.ids.map(async (id) => {
            await httpClient(`${url}/${id}`, {
                method: 'DELETE',
            });
            return id;
        });
        return {data: await Promise.all(tasks)};
    },
});


function sort2orderBy(sort: Sort) {
    const {field, order} = sort;
    if (field) {
        const sign = order === 'ASC' ? '' : '-';
        return {
            'order_by': `${sign}${field}`
        };
    }
    return {};
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
