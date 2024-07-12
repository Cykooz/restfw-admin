import {createRoot} from 'react-dom/client';
import React from 'react';
import './index.css';
import App from './App';
import {AppParams} from "./admin/types";

declare let __RESTFW_ADMIN_PARAMS__: AppParams;

const container = document.getElementById('root');
if (container) {
    const root = createRoot(container);
    root.render(
        <React.StrictMode>
            <App {...__RESTFW_ADMIN_PARAMS__}/>
        </React.StrictMode>
    );
}
