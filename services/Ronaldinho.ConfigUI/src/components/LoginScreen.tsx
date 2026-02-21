import { Box, Center, Heading, Text, VStack, Button } from '@chakra-ui/react';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-hot-toast';

const glassStyle = {
    background: 'rgba(255, 255, 255, 0.03)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '24px',
    boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
};

export const LoginScreen = () => {
    const { login } = useAuth();

    const handleLogin = () => {
        try {
            login();
        } catch (error) {
            toast.error('Falha ao redirecionar para o Keycloak.');
            console.error(error);
        }
    };

    return (
        <Center
            h="100vh"
            bg="#0a0b14"
            backgroundImage="radial-gradient(circle at 50% 50%, #1a1b3a 0%, #0a0b14 100%)"
            fontFamily="'Inter', system-ui, -apple-system, sans-serif"
        >
            <Box p={12} {...glassStyle} maxW="480px" w="full" textAlign="center">
                <VStack gap={8}>
                    <VStack gap={2}>
                        <Heading size="3xl" color="#f1c40f" letterSpacing="4px" fontWeight="900">
                            PHENOMENAL
                        </Heading>
                        <Text color="rgba(255, 255, 255, 0.5)" fontSize="xs" fontWeight="800" letterSpacing="3px">
                            IDENTIFICAÇÃO NEURAL
                        </Text>
                    </VStack>

                    <Text color="rgba(255, 255, 255, 0.7)" fontSize="md" fontWeight="500" lineHeight="1.6">
                        Apenas operadores autorizados podem modificar o sistema nervoso do Ronaldinho.
                    </Text>

                    <Button
                        bg="#f1c40f"
                        color="#0a0b14"
                        size="xl"
                        w="full"
                        h="65px"
                        onClick={handleLogin}
                        fontWeight="900"
                        letterSpacing="2px"
                        _hover={{ bg: 'white', transform: 'scale(1.02)' }}
                        _active={{ transform: 'scale(0.98)' }}
                    >
                        ENTRAR COM KEYCLOAK
                    </Button>

                    <Text fontSize="10px" color="rgba(255, 255, 255, 0.3)" textTransform="uppercase" letterSpacing="2px">
                        Security Layer: OIDC / RS256
                    </Text>
                </VStack>
            </Box>
        </Center>
    );
};
