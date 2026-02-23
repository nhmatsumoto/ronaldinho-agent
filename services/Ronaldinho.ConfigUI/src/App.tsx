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
    geminiApiKey: z.string().optional(),
    openaiApiKey: z.string().optional(),
    anthropicApiKey: z.string().optional(),
    telegramToken: z.string().min(1, 'O Token do Telegram é obrigatório para receber mensagens.'),
    aiModel: z.string().min(1, 'Você deve selecionar uma Engine de IA principal.'),
    personality: z.string().min(20, 'A personalidade base deve ser descritiva e ter pelo menos 20 caracteres.'),
    localPermissions: z.boolean(),
    autoFallback: z.boolean(),
});

type FormData = z.infer<typeof schema>;

const glassStyle = {
    background: 'rgba(255, 255, 255, 0.03)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '24px',
    boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
};

const inputStyle = {
    width: '100%',
    padding: '16px',
    borderRadius: '14px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    color: 'white',
    fontSize: '16px',
    outline: 'none',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
};

const labelStyle = {
    display: 'block',
    fontWeight: 700,
    marginBottom: '10px',
    color: '#f1c40f',
    fontSize: '14px',
    textTransform: 'uppercase' as const,
    letterSpacing: '1.5px',
};

function App() {
    const { settings, isLoading, error, fetchSettings, updateSettings } = useSettingsStore();
    const { isAuthenticated, user, logout } = useAuth();

    const {
        register,
        handleSubmit,
        reset,
        control,
        formState: { isSubmitting },
    } = useForm<FormData>({
        resolver: zodResolver(schema),
    });

    useEffect(() => {
        if (!isAuthenticated) return;
        fetchSettings();
    }, [fetchSettings, isAuthenticated]);

    useEffect(() => {
        if (settings) {
            reset({
                geminiApiKey: settings.geminiApiKey || '',
                openaiApiKey: settings.openaiApiKey || '',
                anthropicApiKey: settings.anthropicApiKey || '',
                telegramToken: settings.telegramToken || '',
                aiModel: settings.aiModel || 'gemini',
                personality: settings.personality || 'MANDATO SUPREMO: Você é o Ronaldinho.',
                localPermissions: settings.localPermissions || false,
                autoFallback: settings.autoFallback ?? true,
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
                <Center h="100vh" bg="#0a0b14">
                    <VStack gap={6}>
                        <Spinner size="xl" color="#f1c40f" />
                        <Text color="white" fontWeight="800" fontSize="2xl" letterSpacing="widest">CONECTANDO AO CÉREBRO...</Text>
                    </VStack>
                </Center>
            </ChakraProvider>
        );
    }

    return (
        <ChakraProvider value={defaultSystem}>
            <Toaster position="top-right" />

            <Box
                bg="#0a0b14"
                minH="100vh"
                py={12}
                color="white"
                backgroundImage="radial-gradient(circle at 50% -20%, #1a1b3a 0%, #0a0b14 60%)"
            >
                <Container maxW="container.xl">

                    <Flex justify="space-between" align="center" mb={12}>
                        <VStack align="start" gap={1}>
                            <Heading size="3xl" color="#f1c40f" letterSpacing="widest" fontWeight="900">RONALDINHO</Heading>
                            <Text color="rgba(255, 255, 255, 0.5)" fontSize="sm" fontWeight="800" textTransform="uppercase" letterSpacing="3px">Neural Core Governance</Text>
                        </VStack>

                        <Flex align="center" gap={4} p={3} {...glassStyle} borderRadius="99px">
                            {user?.picture && <img src={user.picture} alt="Profile" style={{ width: 44, height: 44, borderRadius: '50%', border: '2px solid #f1c40f' }} />}
                            <Box pr={4}>
                                <Text fontSize="sm" fontWeight="900" color="white">{user?.name?.toUpperCase()}</Text>
                                <Button size="xs" variant="plain" color="#f1c40f" _hover={{ textDecoration: 'none', color: 'white' }} onClick={logout}>SIGNOUT</Button>
                            </Box>
                        </Flex>
                    </Flex>

                    <Grid templateColumns={{ base: "1fr", lg: "1fr 2fr" }} gap={10}>

                        {/* LEFT COLUMN: STATUS OVERVIEW */}
                        <VStack gap={8} align="stretch">
                            <Box p={8} {...glassStyle}>
                                <Heading size="md" mb={8} color="#f1c40f" letterSpacing="2px" textTransform="uppercase">Status de Rede</Heading>

                                <VStack align="stretch" gap={6}>
                                    <Box>
                                        <Text fontSize="10px" fontWeight="900" color="rgba(255, 255, 255, 0.4)" mb={2} letterSpacing="2px">ENGINE ATIVA</Text>
                                        <Flex align="center" gap={3}>
                                            <Box w={2} h={2} borderRadius="full" bg="#2ecc71" boxShadow="0 0 10px #2ecc71" />
                                            <Text fontSize="xl" fontWeight="900" textShadow="0 0 10px rgba(241, 196, 15, 0.3)">{settings?.aiModel?.toUpperCase()}</Text>
                                        </Flex>
                                    </Box>

                                    <Box>
                                        <Text fontSize="10px" fontWeight="900" color="rgba(255, 255, 255, 0.4)" mb={2} letterSpacing="2px">SISTEMA DE RESILIÊNCIA</Text>
                                        <Text fontSize="lg" fontWeight="800" color={settings?.autoFallback ? "#2ecc71" : "#e67e22"}>
                                            {settings?.autoFallback ? 'PHENOMENAL FALLBACK ACTIVE' : 'MANUAL OVERRIDE'}
                                        </Text>
                                    </Box>

                                    <Grid templateColumns="repeat(2, 1fr)" gap={4} pt={4}>
                                        <Box p={4} borderRadius="16px" bg="rgba(255, 255, 255, 0.05)" border="1px solid rgba(255, 255, 255, 0.05)">
                                            <Text fontSize="9px" fontWeight="900" color="rgba(255, 255, 255, 0.4)" mb={1}>GEMINI</Text>
                                            <Text fontSize="xs" fontWeight="900" color={settings?.geminiApiKey ? "#2ecc71" : "#e74c3c"}>{settings?.geminiApiKey ? 'SYNCED' : 'OFFLINE'}</Text>
                                        </Box>
                                        <Box p={4} borderRadius="16px" bg="rgba(255, 255, 255, 0.05)" border="1px solid rgba(255, 255, 255, 0.05)">
                                            <Text fontSize="9px" fontWeight="900" color="rgba(255, 255, 255, 0.4)" mb={1}>OPENAI</Text>
                                            <Text fontSize="xs" fontWeight="900" color={settings?.openaiApiKey ? "#2ecc71" : "#e74c3c"}>{settings?.openaiApiKey ? 'SYNCED' : 'OFFLINE'}</Text>
                                        </Box>
                                        <Box p={4} borderRadius="16px" bg="rgba(255, 255, 255, 0.05)" border="1px solid rgba(255, 255, 255, 0.05)">
                                            <Text fontSize="9px" fontWeight="900" color="rgba(255, 255, 255, 0.4)" mb={1}>CLAUDE</Text>
                                            <Text fontSize="xs" fontWeight="900" color={settings?.anthropicApiKey ? "#2ecc71" : "#e74c3c"}>{settings?.anthropicApiKey ? 'SYNCED' : 'OFFLINE'}</Text>
                                        </Box>
                                        <Box p={4} borderRadius="16px" bg="rgba(255, 255, 255, 0.05)" border="1px solid rgba(255, 255, 255, 0.05)">
                                            <Text fontSize="9px" fontWeight="900" color="rgba(255, 255, 255, 0.4)" mb={1}>TELEGRAM</Text>
                                            <Text fontSize="xs" fontWeight="900" color={settings?.telegramToken ? "#2ecc71" : "#e74c3c"}>{settings?.telegramToken ? 'CONNECTED' : 'WAITING'}</Text>
                                        </Box>
                                    </Grid>
                                </VStack>
                            </Box>

                            <Box p={8} {...glassStyle} borderLeft="4px solid #f1c40f">
                                <Text fontSize="10px" fontWeight="900" color="#f1c40f" mb={4} letterSpacing="3px">CURRENT ARCHETYPE</Text>
                                <Text fontSize="sm" color="rgba(255, 255, 255, 0.8)" lineClamp={5} fontStyle="italic" lineHeight="1.6">
                                    "{settings?.personality || 'Waiting for core synchronization...'}"
                                </Text>
                            </Box>
                        </VStack>

                        {/* RIGHT COLUMN: CONTROL PANEL */}
                        <Box p={10} {...glassStyle}>
                            <form onSubmit={handleSubmit(onSubmit)}>
                                <VStack align="stretch" gap={12}>

                                    <Box>
                                        <Heading size="md" mb={8} color="#f1c40f" letterSpacing="2px" textTransform="uppercase">1. Neural Architecture</Heading>
                                        <VStack align="stretch" gap={8}>
                                            <Box>
                                                <label style={labelStyle}>Mestre do Conhecimento (Engine)</label>
                                                <select
                                                    style={inputStyle}
                                                    {...register('aiModel')}
                                                >
                                                    <option value="gemini" style={{ background: '#0a0b14' }}>GOOGLE GEMINI 2.0 FLASH</option>
                                                    <option value="openai" style={{ background: '#0a0b14' }}>OPENAI GPT-4O (ULTRA)</option>
                                                    <option value="claude" style={{ background: '#0a0b14' }}>ANTHROPIC CLAUDE 3.5 SONNET</option>
                                                </select>
                                            </Box>

                                            <Grid templateColumns={{ base: "1fr", md: "1fr 1fr" }} gap={6}>
                                                <Box>
                                                    <label style={labelStyle}>Gemini Key</label>
                                                    <input type="password" style={inputStyle} {...register('geminiApiKey')} />
                                                </Box>
                                                <Box>
                                                    <label style={labelStyle}>OpenAI Key</label>
                                                    <input type="password" style={inputStyle} {...register('openaiApiKey')} />
                                                </Box>
                                                <Box gridColumn="span 2">
                                                    <label style={labelStyle}>Anthropic Key</label>
                                                    <input type="password" style={inputStyle} {...register('anthropicApiKey')} />
                                                </Box>
                                            </Grid>
                                        </VStack>
                                    </Box>

                                    <Box>
                                        <Heading size="md" mb={8} color="#f1c40f" letterSpacing="2px" textTransform="uppercase">2. Módulo de Personalidade (SOUL)</Heading>
                                        <textarea
                                            style={{ ...inputStyle, minHeight: '160px', fontFamily: 'monospace' }}
                                            {...register('personality')}
                                        />
                                    </Box>

                                    <Box>
                                        <Heading size="md" mb={8} color="#f1c40f" letterSpacing="2px" textTransform="uppercase">3. Protocolos de Segurança</Heading>
                                        <VStack align="stretch" gap={8}>
                                            <Box>
                                                <label style={labelStyle}>Telegram Bot Gateway</label>
                                                <input type="password" style={inputStyle} {...register('telegramToken')} />
                                            </Box>

                                            <Flex gap={8}>
                                                <Flex align="center" gap={4} p={4} borderRadius="16px" bg="rgba(241, 196, 15, 0.05)" border="1px solid rgba(241, 196, 15, 0.1)" flex={1}>
                                                    <Controller
                                                        name="autoFallback"
                                                        control={control}
                                                        render={({ field }) => (
                                                            <input
                                                                type="checkbox"
                                                                style={{ width: '22px', height: '22px', accentColor: '#f1c40f' }}
                                                                checked={field.value}
                                                                onChange={(e) => field.onChange(e.target.checked)}
                                                            />
                                                        )}
                                                    />
                                                    <Box>
                                                        <Text fontWeight="800" fontSize="xs" color="#f1c40f">PHENO FALLBACK</Text>
                                                        <Text fontSize="10px" color="rgba(255, 255, 255, 0.5)">Resiliência Anti-429</Text>
                                                    </Box>
                                                </Flex>

                                                <Flex align="center" gap={4} p={4} borderRadius="16px" bg="rgba(46, 204, 113, 0.05)" border="1px solid rgba(46, 204, 113, 0.1)" flex={1}>
                                                    <Controller
                                                        name="localPermissions"
                                                        control={control}
                                                        render={({ field }) => (
                                                            <input
                                                                type="checkbox"
                                                                style={{ width: '22px', height: '22px', accentColor: '#2ecc71' }}
                                                                checked={field.value}
                                                                onChange={(e) => field.onChange(e.target.checked)}
                                                            />
                                                        )}
                                                    />
                                                    <Box>
                                                        <Text fontWeight="800" fontSize="xs" color="#2ecc71">LOCAL ACCESS</Text>
                                                        <Text fontSize="10px" color="rgba(255, 255, 255, 0.5)">Escrita em Disco</Text>
                                                    </Box>
                                                </Flex>
                                            </Flex>
                                        </VStack>
                                    </Box>


                                    {(errors.aiModel || errors.personality || errors.telegramToken) && (
                                        <Box p={4} borderRadius="12px" bg="rgba(231, 76, 60, 0.1)" border="1px solid rgba(231, 76, 60, 0.35)">
                                            {errors.aiModel?.message && <Text color="#ffb3b3" fontSize="sm">• {errors.aiModel.message}</Text>}
                                            {errors.personality?.message && <Text color="#ffb3b3" fontSize="sm">• {errors.personality.message}</Text>}
                                            {errors.telegramToken?.message && <Text color="#ffb3b3" fontSize="sm">• {errors.telegramToken.message}</Text>}
                                        </Box>
                                    )}

                                    <Button
                                        bg="#f1c40f"
                                        color="#0a0b14"
                                        size="xl"
                                        h="70px"
                                        fontSize="lg"
                                        fontWeight="900"
                                        letterSpacing="4px"
                                        _hover={{ bg: 'white', transform: 'scale(1.02)' }}
                                        _active={{ transform: 'scale(0.98)' }}
                                        loading={isSubmitting || isLoading}
                                        type="submit"
                                    >
                                        SYNC COGNITION
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
