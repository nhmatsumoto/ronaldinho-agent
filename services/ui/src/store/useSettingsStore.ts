import { create } from 'zustand';
import { AgentSettings, SettingsService } from '../api/SettingsService';

interface SettingsState {
    settings: AgentSettings | null;
    isLoading: boolean;
    error: string | null;

    fetchSettings: () => Promise<void>;
    updateSettings: (newSettings: AgentSettings) => Promise<void>;
}

export const useSettingsStore = create<SettingsState>((set) => ({
    settings: null,
    isLoading: false,
    error: null,

    fetchSettings: async () => {
        set({ isLoading: true, error: null });
        try {
            const data = await SettingsService.getSettings();
            set({ settings: data, isLoading: false });
        } catch (err: any) {
            set({ error: err.message || 'Falha ao buscar configurações', isLoading: false });
        }
    },

    updateSettings: async (newSettings: AgentSettings) => {
        set({ isLoading: true, error: null });
        try {
            await SettingsService.updateSettings(newSettings);
            set({ settings: newSettings, isLoading: false });
        } catch (err: any) {
            set({ error: err.message || 'Falha ao salvar configurações', isLoading: false });
            throw err; // Re-throw to be caught by the UI component
        }
    }
}));
