import { useEffect } from 'react';
import {
    ChakraProvider, defaultSystem, Box, Heading, VStack, Button, Container, Text,
    Spinner, Center, Flex, Grid
} from '@chakra-ui/react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Toaster, toast } from 'react-hot-toast';
import { useSettingsStore } from './store/useSettingsStore';
import { useAuth } from './contexts/AuthContext';
import { LoginScreen } from './components/LoginScreen';

// Define the validation schema using Zod
const schema = z.object({
    geminiApiKey: z.string().min(1, 'A API Key é obrigatória para conectar ao provedor.'),
    telegramToken: z.string().min(1, 'O Token do Telegram é obrigatório para receber mensagens.'),
    aiModel: z.string().min(1, 'Você deve selecionar uma Engine de IA principal.'),
    personality: z.string().min(20, 'A personalidade base deve ser descritiva e ter pelo menos 20 caracteres.'),
    localPermissions: z.boolean(),
});

type FormData = z.infer<typeof schema>;

// --- Helper CSS Classes for Premium Native Inputs ---
const inputStyle = {
    width: '100%',
    padding: '14px',
    borderRadius: '10px',
    border: '1px solid #CBD5E0',
    backgroundColor: '#F7FAFC',
    fontSize: '16px',
    outline: 'none',
    transition: 'all 0.2s ease-in-out',
    boxShadow: 'inset 0 1px 2px rgba(0, 0, 0, 0.05)',
};

const inputErrorStyle = {
    ...inputStyle,
    border: '2px solid #E53E3E',
    backgroundColor: '#FFF5F5',
};

const labelStyle = {
    display: 'block',
    fontWeight: 700,
    marginBottom: '8px',
    color: '#2D3748',
    fontSize: '15px',
    letterSpacing: '0.3px',
};

const errorTextStyle = {
    color: '#E53E3E',
    fontSize: '13px',
    marginTop: '6px',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
};

function App() {
    const { settings, isLoading, error, fetchSettings, updateSettings } = useSettingsStore();
    const { isAuthenticated, user, logout } = useAuth();

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
        const toastId = toast.loading('Sincronizando Mente do Agente...');
        try {
            await updateSettings(data);
            toast.success('Configurações salvas com sucesso no Core!', { id: toastId, duration: 4000 });
        } catch (err: any) {
            toast.error('Falha de Sincronização: ' + (err.message || error || 'Erro desconhecido.'), { id: toastId, duration: 5000 });
        }
    };

    if (!isAuthenticated) {
        return (
            <ChakraProvider value={defaultSystem}>
                <Toaster position="top-right" />
                <LoginScreen />
            </ChakraProvider>
        );
    }

    if (isLoading && !settings) {
        return (
            <ChakraProvider value={defaultSystem}>
                <Center h="100vh" bg="gray.50">
                    <VStack gap={4}>
                        <Spinner size="xl" color="blue.500" />
                        <Text color="gray.600" fontWeight="600" fontSize="lg">Conectando ao Ronaldinho Neural Core...</Text>
                    </VStack>
                </Center>
            </ChakraProvider>
        );
    }

    return (
        <ChakraProvider value={defaultSystem}>
            <Toaster position="top-right" />

            <Box bg="gray.100" minH="100vh" py={12} fontFamily="system-ui, -apple-system, sans-serif">
                <Container maxW="container.lg">

                    <Box textAlign="center" mb={6} position="relative">
                        <Heading size="2xl" color="blue.800" letterSpacing="tight" fontWeight="800">Ronaldinho Governance</Heading>
                        <Text color="gray.600" mt={3} fontSize="xl" fontWeight="500">Controle Operacional Central do Agente Neural</Text>

                        <Flex position="absolute" top={0} right={0} align="center" gap={3} bg="white" p={2} borderRadius={10} boxShadow="sm" border="1px solid" borderColor="gray.200">
                            {user?.picture && <img src={user.picture} alt="Profile" style={{ width: 32, height: 32, borderRadius: '50%' }} />}
                            <Box textAlign="right" display={{ base: 'none', md: 'block' }}>
                                <Text fontSize="xs" fontWeight="bold" color="blue.700">{user?.name}</Text>
                                <Button size="xs" variant="ghost" colorScheme="red" h="auto" p={0} mt={0.5} onClick={logout}>Desconectar</Button>
                            </Box>
                        </Flex>
                    </Box>

                    <Grid templateColumns={{ base: "1fr", lg: "1fr 2fr" }} gap={8}>

                        {/* LEFT COLUMN: CURRENT STATE */}
                        <Box>
                            <Box p={6} borderWidth={1} borderRadius={16} boxShadow="md" bg="white" position="sticky" top="20px">
                                <Heading size="md" mb={6} color="gray.800" borderBottom="2px solid" borderColor="blue.100" pb={3}>
                                    Status Atual (Ativo)
                                </Heading>

                                <VStack align="stretch" gap={5}>
                                    <Box>
                                        <Text fontSize="xs" fontWeight="700" color="gray.500" textTransform="uppercase" letterSpacing="wider">Engine Selecionada</Text>
                                        <Text fontSize="md" fontWeight="600" color="blue.600">{settings?.aiModel.toUpperCase() || 'NÃO CONFIGURADO'}</Text>
                                    </Box>

                                    <Box>
                                        <Text fontSize="xs" fontWeight="700" color="gray.500" textTransform="uppercase" letterSpacing="wider">Permissão Local (SuperToolbox)</Text>
                                        <Flex align="center" gap={2} mt={1}>
                                            <Box w={3} h={3} borderRadius="50%" bg={settings?.localPermissions ? "green.400" : "red.400"} />
                                            <Text fontSize="sm" fontWeight="600" color={settings?.localPermissions ? "green.600" : "red.600"}>
                                                {settings?.localPermissions ? 'HABILITADO (Mutável)' : 'BLOQUEADO (Apenas Leitura)'}
                                            </Text>
                                        </Flex>
                                    </Box>

                                    <Box>
                                        <Text fontSize="xs" fontWeight="700" color="gray.500" textTransform="uppercase" letterSpacing="wider">API Keys Configúradas</Text>
                                        <Text fontSize="sm" fontWeight="600" color="gray.700">
                                            LLM: {settings?.geminiApiKey ? '✅ Salva' : '❌ Ausente'}
                                            <br />
                                            Telegram: {settings?.telegramToken ? '✅ Salva' : '❌ Ausente'}
                                        </Text>
                                    </Box>

                                    <Box>
                                        <Text fontSize="xs" fontWeight="700" color="gray.500" textTransform="uppercase" letterSpacing="wider">Snapshot de Personalidade</Text>
                                        <Text fontSize="sm" color="gray.600" lineClamp={4} fontStyle="italic" bg="gray.50" p={3} borderRadius={8} border="1px solid" borderColor="gray.200">
                                            "{settings?.personality || 'Sem diretriz definida...'}"
                                        </Text>
                                    </Box>
                                </VStack>
                            </Box>
                        </Box>

                        {/* RIGHT COLUMN: CONFIG FORM */}
                        <Box p={8} borderWidth={1} borderRadius={16} boxShadow="xl" bg="white">
                            <form onSubmit={handleSubmit(onSubmit)}>
                                <VStack align="stretch" gap={10}>

                                    {/* SECTION 1: MODEL */}
                                    <Box>
                                        <Heading size="sm" mb={5} color="blue.700" textTransform="uppercase" letterSpacing="widest" fontWeight="800">
                                            1. Roteamento de Cérebro (Brain)
                                        </Heading>

                                        <Grid templateColumns={{ base: "1fr", md: "1fr 1fr" }} gap={6}>
                                            <Box>
                                                <label style={labelStyle}>Engine de IA Principal</label>
                                                <select
                                                    style={errors.aiModel ? inputErrorStyle : inputStyle}
                                                    {...register('aiModel')}
                                                >
                                                    <option value="gemini">Google Gemini 2.0 Flash</option>
                                                    <option value="openai">OpenAI GPT-4o</option>
                                                    <option value="claude">Anthropic Claude 3.5 Sonnet</option>
                                                </select>
                                                {errors.aiModel && <span style={errorTextStyle}>⚠️ {errors.aiModel.message}</span>}
                                            </Box>

                                            <Box>
                                                <label style={labelStyle}>Chave Privada (API Key)</label>
                                                <input
                                                    type="password"
                                                    style={errors.geminiApiKey ? inputErrorStyle : inputStyle}
                                                    placeholder="Insira a API Key..."
                                                    {...register('geminiApiKey')}
                                                />
                                                {errors.geminiApiKey && <span style={errorTextStyle}>⚠️ {errors.geminiApiKey.message}</span>}
                                            </Box>
                                        </Grid>
                                    </Box>

                                    <Box borderBottom="1px solid" borderColor="gray.100" />

                                    {/* SECTION 2: PERSONALITY */}
                                    <Box>
                                        <Heading size="sm" mb={5} color="blue.700" textTransform="uppercase" letterSpacing="widest" fontWeight="800">
                                            2. Identidade e Comportamento
                                        </Heading>
                                        <Box>
                                            <label style={labelStyle}>Arquivo SOUL.md - Quem é o Ronaldinho?</label>
                                            <textarea
                                                style={{ ...(errors.personality ? inputErrorStyle : inputStyle), minHeight: '180px', fontFamily: 'monospace', lineHeight: 1.5 }}
                                                placeholder="Defina o prompt sistêmico central do agente..."
                                                {...register('personality')}
                                            />
                                            {errors.personality && <span style={errorTextStyle}>⚠️ {errors.personality.message}</span>}
                                            <Text fontSize="xs" color="gray.500" mt={2}>
                                                Esta será a principal diretriz de comportamento para todas as interações.
                                            </Text>
                                        </Box>
                                    </Box>

                                    <Box borderBottom="1px solid" borderColor="gray.100" />

                                    {/* SECTION 3: PERMISSIONS */}
                                    <Box>
                                        <Heading size="sm" mb={5} color="blue.700" textTransform="uppercase" letterSpacing="widest" fontWeight="800">
                                            3. Permissões de Host
                                        </Heading>
                                        <VStack align="stretch" gap={6}>
                                            <Box>
                                                <label style={labelStyle}>Telegram Bot Token (Ingresso de Rede)</label>
                                                <input
                                                    type="password"
                                                    style={errors.telegramToken ? inputErrorStyle : inputStyle}
                                                    placeholder="123456789:ABCdef..."
                                                    {...register('telegramToken')}
                                                />
                                                {errors.telegramToken && <span style={errorTextStyle}>⚠️ {errors.telegramToken.message}</span>}
                                            </Box>

                                            <Flex bg={errors.localPermissions ? "red.50" : "blue.50"} p={5} borderRadius="12px" borderWidth="1px" borderColor={errors.localPermissions ? "red.200" : "blue.200"} alignItems="center">
                                                <Controller
                                                    name="localPermissions"
                                                    control={control}
                                                    render={({ field }) => (
                                                        <input
                                                            type="checkbox"
                                                            id="localPermissions"
                                                            style={{ width: '28px', height: '28px', cursor: 'pointer', accentColor: '#3182ce' }}
                                                            checked={field.value}
                                                            onChange={(e) => field.onChange(e.target.checked)}
                                                        />
                                                    )}
                                                />
                                                <Box ml={4}>
                                                    <label htmlFor="localPermissions" style={{ ...labelStyle, marginBottom: 0, color: '#2B6CB0', fontSize: '16px' }}>
                                                        Autorizar Mutações no Disco (SuperToolbox)
                                                    </label>
                                                    <Text fontSize="sm" color="gray.600" mt={1}>
                                                        Se marcado, o agente poderá editar arquivos, executar comandos Bash e realizar commits na pasta do projeto via `mcp`.
                                                    </Text>
                                                </Box>
                                            </Flex>
                                        </VStack>
                                    </Box>

                                    <Button
                                        colorScheme="blue"
                                        size="lg"
                                        h="64px"
                                        fontSize="lg"
                                        fontWeight="bold"
                                        mt={4}
                                        type="submit"
                                        boxShadow="xl"
                                        _hover={{ transform: 'translateY(-2px)', boxShadow: '2xl' }}
                                        _active={{ transform: 'translateY(1px)' }}
                                        loading={isSubmitting || isLoading}
                                        loadingText="Processando Mutação..."
                                    >
                                        GRAVAR CONFIGURAÇÕES NO NÚCLEO
                                    </Button>
                                </VStack>
                            </form>
                        </Box>
                    </Grid>
                </Container>
            </Box>
        </ChakraProvider>
    );
}

export default App;

