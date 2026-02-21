import { Box, Center, Heading, Text, VStack, Button } from '@chakra-ui/react';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-hot-toast';

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
        <Center h="100vh" bg="gray.100" fontFamily="system-ui, -apple-system, sans-serif">
            <Box p={10} rounded="xl" bg="white" boxShadow="2xl" maxW="450px" w="full" textAlign="center">
                <VStack gap={6}>
                    <Box>
                        <Heading size="xl" color="blue.800" letterSpacing="tight" fontWeight="900" mb={2}>
                            Identificação Neural
                        </Heading>
                        <Text color="gray.500" fontSize="md" fontWeight="500">
                            Apenas operadores autorizados podem modificar o sistema nervoso do Ronaldinho.
                        </Text>
                    </Box>

                    <Box w="full" bg="gray.50" p={6} borderRadius="lg" border="1px dashed" borderColor="gray.300">
                        <Button
                            colorScheme="blue"
                            size="lg"
                            w="full"
                            onClick={handleLogin}
                            boxShadow="md"
                        >
                            Entrar com Keycloak
                        </Button>
                    </Box>

                    <Text fontSize="xs" color="gray.400" mt={4}>
                        Autenticação auditada por sessão corporativa.
                    </Text>
                </VStack>
            </Box>
        </Center>
    );
};
