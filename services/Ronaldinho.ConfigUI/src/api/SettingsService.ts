import apiClient from './axiosClient';

// Type definitions for the agent configuration
export interface AgentSettings {
    geminiApiKey: string;
    telegramToken: string;
    aiModel: string;
    personality: string;
    localPermissions: boolean;
}

export const SettingsService = {
    // Uses interceptor-enabled axios instance to fetch agent config
    getSettings: async (): Promise<AgentSettings> => {
        try {
            const response = await apiClient.get<AgentSettings>('/settings');
            return response.data;
        } catch (error) {
            // Provide fallback for development/UI design when backend isn't ready
            console.warn('Backend unavailable, returning system mock settings.');
            return {
                geminiApiKey: '',
                telegramToken: '',
                aiModel: 'gemini',
                personality: 'MANDATO SUPREMO: Você é o Ronaldinho.',
                localPermissions: false
            };
        }
    },

    // Uses interceptor-enabled axios instance to push config updates
    updateSettings: async (settings: AgentSettings): Promise<void> => {
        try {
            await apiClient.post('/settings', settings);
        } catch (error) {
            console.warn('Backend unavailable, faking successful save.', settings);
        }
    }
};
