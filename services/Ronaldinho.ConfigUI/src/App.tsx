import { useEffect } from 'react';
import {
    ChakraProvider, defaultSystem, Box, Heading, VStack, Button, Container, Text,
    Spinner, Center, Flex
} from '@chakra-ui/react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useSettingsStore } from './store/useSettingsStore';

// Define the validation schema using Zod
const schema = z.object({
    geminiApiKey: z.string(),
    telegramToken: z.string(),
    aiModel: z.string().min(1, 'Selecione um modelo de IA.'),
    personality: z.string().min(10, 'A personalidade base deve ter pelo menos 10 caracteres explicativos.'),
    localPermissions: z.boolean(),
});

type FormData = z.infer<typeof schema>;

// --- Helper CSS Classes for Native Inputs ---
const inputStyle = {
    width: '100%',
    padding: '12px',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
    backgroundColor: '#FFFFFF',
    fontSize: '16px',
    outline: 'none',
    transition: 'border-color 0.2s',
};

const labelStyle = {
    display: 'block',
    fontWeight: 600,
    marginBottom: '8px',
    color: '#2D3748',
    fontSize: '14px',
};

const errorStyle = {
    color: '#E53E3E',
    fontSize: '12px',
    marginTop: '4px',
};


function App() {
    const { settings, isLoading, error, fetchSettings, updateSettings } = useSettingsStore();

    const {
        register,
        handleSubmit,
        reset,
        control,
        formState: { errors, isSubmitting },
    } = useForm<FormData>({
        resolver: zodResolver(schema),
    });

    useEffect(() => {
        fetchSettings();
    }, [fetchSettings]);

    useEffect(() => {
        if (settings) {
            reset({
                geminiApiKey: settings.geminiApiKey || '',
                telegramToken: settings.telegramToken || '',
                aiModel: settings.aiModel || 'gemini',
                personality: settings.personality || 'MANDATO SUPREMO: Você é o Ronaldinho.',
                localPermissions: settings.localPermissions || false,
            });
        }
    }, [settings, reset]);

    const onSubmit = async (data: FormData) => {
        try {
            await updateSettings(data);
            alert('Sucesso: Configurações validadas e sincronizadas. (Reinicie o Backend C#).');
        } catch (err: any) {
            alert('Erro de Sincronização: ' + (err.message || error || 'Falha ao salvar.'));
        }
    };

    if (isLoading && !settings) {
        return (
            <ChakraProvider value={defaultSystem}>
                <Center h="100vh" bg="gray.50">
                    <VStack gap={4}>
                        <Spinner size="xl" color="blue.500" />
                        <Text color="gray.600" fontWeight="500">Sincronizando Mente do Ronaldinho...</Text>
                    </VStack>
                </Center>
            </ChakraProvider>
        );
    }

    return (
        <ChakraProvider value={defaultSystem}>
            <Box bg="gray.50" minH="100vh" py={10}>
                <Container maxW="container.md">
                    <Box p={8} borderWidth={1} borderRadius={12} boxShadow="xl" bg="white">
                        <form onSubmit={handleSubmit(onSubmit)}>
                            <VStack align="stretch" gap={8}>
                                <Box textAlign="center">
                                    <Heading size="xl" color="blue.700" letterSpacing="tight">Ronaldinho Neural Console</Heading>
                                    <Text color="gray.500" mt={2} fontSize="lg">Model, Identity & Permissions Governance</Text>
                                </Box>

                                <Box borderBottom="1px solid" borderColor="gray.200" />

                                {/* SECTION 1: MODEL */}
                                <Box>
                                    <Heading size="sm" mb={4} color="gray.700" textTransform="uppercase" letterSpacing="widest">1. Modelo Mestre (Brain Routing)</Heading>
                                    <VStack align="stretch" gap={4}>
                                        <Box>
                                            <label style={labelStyle}>Engine de IA Principal</label>
                                            <select style={inputStyle} {...register('aiModel')}>
                                                <option value="gemini">Google Gemini 3.1 Pro (Multimodal Ágil)</option>
                                                <option value="openai">OpenAI GPT-4o / GPT-OS 120B (Análise Profunda)</option>
                                                <option value="claude">Anthropic Claude 3.5 Sonnet (Refatoração Nativa)</option>
                                                <option value="codex">OpenAI Codex (Geração de Testes)</option>
                                            </select>
                                            {errors.aiModel && <div style={errorStyle}>{errors.aiModel.message}</div>}
                                        </Box>

                                        <Box>
                                            <label style={labelStyle}>Chave Privada do Modelo</label>
                                            <input
                                                type="password"
                                                style={inputStyle}
                                                placeholder="Insira a API Key do provedor selecionado..."
                                                {...register('geminiApiKey')}
                                            />
                                            {errors.geminiApiKey && <div style={errorStyle}>{errors.geminiApiKey.message}</div>}
                                        </Box>
                                    </VStack>
                                </Box>

                                {/* SECTION 2: PERSONALITY */}
                                <Box>
                                    <Heading size="sm" mb={4} color="gray.700" textTransform="uppercase" letterSpacing="widest">2. SOUL.md (Personalidade e Estilo)</Heading>
                                    <Box>
                                        <label style={labelStyle}>Quem é o Ronaldinho? Contexto Injetado</label>
                                        <textarea
                                            style={{ ...inputStyle, minHeight: '150px', fontFamily: 'monospace' }}
                                            placeholder="Defina o prompt sistêmico central do agente..."
                                            {...register('personality')}
                                        />
                                        {errors.personality && <div style={errorStyle}>{errors.personality.message}</div>}
                                    </Box>
                                </Box>

                                {/* SECTION 3: PERMISSIONS */}
                                <Box>
                                    <Heading size="sm" mb={4} color="gray.700" textTransform="uppercase" letterSpacing="widest">3. Permissões de Máquina</Heading>
                                    <VStack align="stretch" gap={4}>
                                        <Box>
                                            <label style={labelStyle}>Telegram Bot Token (Ingresso de Mensagens)</label>
                                            <input
                                                type="password"
                                                style={inputStyle}
                                                placeholder="123456789:ABCdef..."
                                                {...register('telegramToken')}
                                            />
                                        </Box>

                                        <Flex bg="gray.100" p={4} borderRadius="8px" borderWidth="1px" borderColor="gray.200" alignItems="center">
                                            <Controller
                                                name="localPermissions"
                                                control={control}
                                                render={({ field }) => (
                                                    <input
                                                        type="checkbox"
                                                        id="localPermissions"
                                                        style={{ width: '24px', height: '24px', cursor: 'pointer' }}
                                                        checked={field.value}
                                                        onChange={(e) => field.onChange(e.target.checked)}
                                                    />
                                                )}
                                            />
                                            <Box ml={4}>
                                                <label htmlFor="localPermissions" style={{ ...labelStyle, marginBottom: 0, color: '#C53030' }}>
                                                    Habilitar Mutações no Host (SuperToolbox)
                                                </label>
                                                <Text fontSize="sm" color="gray.600">
                                                    Permite que especialistas executem tarefas destrutivas no disco, commitem códigos e analisem diffs localmente.
                                                </Text>
                                            </Box>
                                        </Flex>
                                    </VStack>
                                </Box>

                                <Button
                                    colorScheme="blue"
                                    size="lg"
                                    h="56px"
                                    mt={4}
                                    type="submit"
                                    boxShadow="md"
                                    _hover={{ transform: 'translateY(-2px)', boxShadow: 'lg' }}
                                    loading={isSubmitting || isLoading}
                                    loadingText="Sincronizando com Agent Swarm..."
                                >
                                    Gravar Novas Regras no Core
                                </Button>
                            </VStack>
                        </form>
                    </Box>
                </Container>
            </Box>
        </ChakraProvider>
    );
}

export default App;

