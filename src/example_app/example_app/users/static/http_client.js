function getHttpClient(jsonFetch) {
    const BASIC_TOKEN_KEY = 'rest_admin.auth.basic';

    return function(url, options= {}) {
        if (!options.headers)
        {
            options.headers = new Headers({Accept: 'application/json'});
        }
        let headers = options.headers;
        headers.set('X-Requested-With', 'XMLHttpRequest');

        const basic_token = localStorage.getItem(BASIC_TOKEN_KEY);
        if (basic_token) {
            headers.set('Authorization', `Basic ${basic_token}`);
        }

        return jsonFetch(url, options);
    };
}
