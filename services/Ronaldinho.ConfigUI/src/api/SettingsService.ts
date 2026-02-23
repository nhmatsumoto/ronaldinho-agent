import apiClient from './axiosClient';

// Type definitions for the agent configuration
export interface AgentSettings {
    geminiApiKey?: string;
    openaiApiKey?: string;
    anthropicApiKey?: string;
    telegramToken: string;
    aiModel: string;
    personality: string;
    localPermissions: boolean;
    autoFallback: boolean;
}

export const SettingsService = {
    // Uses interceptor-enabled axios instance to fetch agent config
    getSettings: async (): Promise<AgentSettings> => {
        const response = await apiClient.get<AgentSettings>('/settings');
        return response.data;
    },

    // Uses interceptor-enabled axios instance to push config updates
    updateSettings: async (settings: AgentSettings): Promise<void> => {
        await apiClient.post('/settings', settings);
    }
};
