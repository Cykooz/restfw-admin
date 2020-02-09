import React, {useEffect, useState} from 'react';
import {Admin} from 'react-admin';
import {fetchUtils} from 'ra-core';
import halRestDataProvider from './dataProvider';
import {ApiInfo, IApiInfo} from './apiInfo';
import {getResources} from "./resources";


function httpClient(url: string, options: fetchUtils.Options = {}) {
    if (!options.headers)
        options.headers = new Headers({Accept: 'application/json'});
    const token = localStorage.getItem('token');
    if (token) {
        let headers = options.headers as Headers;
        headers.set('Mountbit-Auth', token);
    }
    return fetchUtils.fetchJson(url, options);
}


const App = () => {
    const [apiInfo, setApiInfo] = useState<IApiInfo | null>(null);

    useEffect(() => {
        async function fetchApiInfo() {
            const url = '/api_info.json';
            const {json}  = await httpClient(url);
            const apiInfoInstance = new ApiInfo(json);
            setApiInfo(
                // GOTCHA: apiInfoInstance can be a function
                () => apiInfoInstance
            );
        }

        fetchApiInfo();
    }, []);

    if (!apiInfo) {
        return (
            <div className="loader-container">
                <div className="loader">Loading...</div>
            </div>
        );
    }

    const dataProvider = halRestDataProvider(apiInfo, httpClient);

    return (
        <Admin
            title={apiInfo.getTitle()}
            dataProvider={dataProvider}
            // authProvider={authProvider}
        >
            {getResources(apiInfo)}
        </Admin>
    );
};

export default App;
