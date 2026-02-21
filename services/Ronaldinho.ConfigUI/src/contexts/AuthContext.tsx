import React, { createContext, useContext, ReactNode } from 'react';
import { useAuth as useOidcAuth } from 'react-oidc-context';

export interface User {
    email: string;
    name: string;
    sub: string;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: () => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const auth = useOidcAuth();

    const user: User | null = auth.user?.profile ? {
        email: auth.user.profile.email as string || '',
        name: auth.user.profile.name as string || '',
        sub: auth.user.profile.sub as string || ''
    } : null;

    const token = auth.user?.access_token || null;

    const login = () => {
        auth.signinRedirect();
    };

    const logout = () => {
        auth.signoutRedirect();
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: auth.isAuthenticated }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
