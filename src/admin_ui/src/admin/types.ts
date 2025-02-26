import {AuthProvider, fetchUtils} from 'ra-core';
import {IApiInfo} from "./apiInfo";
import {IFileUploadProvider} from "./uploadProvider";

export interface IHttpClient {
    (url: string, options?: fetchUtils.Options): Promise<{ status: number, headers: Headers, body: string, json: any }>;
}

export interface IGetAuthProvider {
    (httpClient: IHttpClient, apiInfo: IApiInfo): AuthProvider
}

export interface IGetHttpClient {
    (fetchJson: IHttpClient): IHttpClient
}

export interface IGetFileUploadProvider {
    (httpClient: IHttpClient, apiInfo: IApiInfo): IFileUploadProvider
}

export type AppParams = {
    apiInfoUrl: string,
    getAuthProvider?: IGetAuthProvider,
    getHttpClient?: IGetHttpClient,
    getFileUploadProvider?: IGetFileUploadProvider,
};
