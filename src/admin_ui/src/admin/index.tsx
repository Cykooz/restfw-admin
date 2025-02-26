import {useEffect, useState} from 'react';
import {Admin} from 'react-admin';
import {fetchUtils} from 'ra-core';
import halRestDataProvider from './dataProvider';
import {ApiInfo, IApiInfo} from './apiInfo';
import {getResources} from "./resources";
import {AppParams} from "./types";
import {DefaultFileUploadProvider} from "./uploadProvider";


function defaultHttpClient(url: string, options: fetchUtils.Options = {}) {
    if (!options.headers)
        options.headers = new Headers({Accept: 'application/json'});
    const headers = options.headers as Headers;
    headers.set('X-Requested-With', 'XMLHttpRequest');
    return fetchUtils.fetchJson(url, options);
}


function App(appParams: AppParams) {
    const [apiInfo, setApiInfo] = useState<IApiInfo | null>(null);

    useEffect(() => {
        async function fetchApiInfo() {
            const {json} = await defaultHttpClient(appParams.apiInfoUrl);
            const apiInfoInstance = new ApiInfo(json);
            setApiInfo(
                // GOTCHA: apiInfoInstance can be a function
                () => apiInfoInstance
            );
        }

        fetchApiInfo();
    }, [appParams]);

    if (!apiInfo) {
        return (
            <div className="loader-container">
                <div className="loader">Loading...</div>
            </div>
        );
    }

    const authProvider = appParams.getAuthProvider?.(defaultHttpClient, apiInfo);
    const httpClient = appParams.getHttpClient?.(fetchUtils.fetchJson) ?? defaultHttpClient;
    const fileUploadProvider = appParams.getFileUploadProvider?.(httpClient, apiInfo) ?? new DefaultFileUploadProvider();
    const dataProvider = halRestDataProvider(apiInfo, fileUploadProvider, httpClient);

    document.title = apiInfo.getTitle();

    return (
        <Admin
            title={apiInfo.getTitle()}
            dataProvider={dataProvider}
            authProvider={authProvider}
            disableTelemetry={true}
        >
            {getResources(apiInfo)}
        </Admin>
    );
}

export default App;

