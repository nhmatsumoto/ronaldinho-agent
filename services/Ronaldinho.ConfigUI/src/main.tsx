import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { AuthProvider as OidcProvider } from 'react-oidc-context';
import { AuthProvider as ConfigUIAuthProvider } from './contexts/AuthContext';

const oidcConfig = {
    authority: import.meta.env.VITE_AUTH_AUTHORITY || "http://localhost:8080/realms/ronaldinho",
    client_id: import.meta.env.VITE_AUTH_CLIENT_ID || "configui-client",
    redirect_uri: import.meta.env.VITE_AUTH_REDIRECT_URI || window.location.origin,
};

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <OidcProvider {...oidcConfig}>
            <ConfigUIAuthProvider>
                <App />
            </ConfigUIAuthProvider>
        </OidcProvider>
    </React.StrictMode>,
);
