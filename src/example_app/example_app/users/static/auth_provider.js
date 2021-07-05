function getBasicAuthProvider(httpClient, apiInfo) {
    const BASIC_TOKEN_KEY = 'rest_admin.auth.basic';

    return {
        login: function({username, password}) {
            const basic = btoa(`${username}:${password}`);
            localStorage.setItem(BASIC_TOKEN_KEY, basic);
            return Promise.resolve();
        },
        logout: function() {
            localStorage.removeItem(BASIC_TOKEN_KEY);
            return Promise.resolve();
        },
        checkAuth: function() {
            if (!localStorage.getItem(BASIC_TOKEN_KEY)) {
                return Promise.reject();
            }
            return Promise.resolve();
        },
        checkError: function(error) {
            const status = error.status;
            if (status === 401 || status === 403) {
                localStorage.removeItem(BASIC_TOKEN_KEY);
                return Promise.reject();
            }
            return Promise.resolve();
        },
        getPermissions: function(params) {
            return Promise.resolve();
        },
    };
}
