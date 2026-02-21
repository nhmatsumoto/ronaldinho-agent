import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { AuthProvider as OidcProvider } from 'react-oidc-context';
import { AuthProvider as ConfigUIAuthProvider } from './contexts/AuthContext';

const oidcConfig = {
    authority: "http://localhost:8080/realms/ronaldinho",
    client_id: "configui-client",
    redirect_uri: "http://localhost:5173",
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
