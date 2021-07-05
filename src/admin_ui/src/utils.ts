
/* eslint-disable no-console */
export function log(type, resource, params: any[], response: any) {
    // if (console.group) {
        // Better logging in Chrome
        console.groupCollapsed(type, resource, JSON.stringify(params));
        console.log(response);
        console.groupEnd();
    // } else {
    //     console.log('FakeRest request ', type, resource, params);
    //     console.log('FakeRest response', response);
    // }
}
