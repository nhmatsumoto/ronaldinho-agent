using System.ComponentModel;
using Microsoft.SemanticKernel;

namespace Ronaldinho.NeuralCore.Services.Auth;

public class AuthSkill
{
    private readonly GoogleAuthService _googleAuth;

    public AuthSkill(GoogleAuthService googleAuth)
    {
        _googleAuth = googleAuth;
    }

    [KernelFunction, Description("Solicita autenticação do usuário no Google (OAuth2) para acessar Drive/Calendar.")]
    public async Task<string> LoginGoogle()
    {
        try
        {
            var credential = await _googleAuth.AuthenticateAsync();
            if (credential != null && credential.Token != null)
            {
                return "✅ Autenticação Google realizada com sucesso! Token seguro e criptografado (DPAPI).";
            }
            else
            {
                return "❌ Falha na autenticação ou cancelado pelo usuário.";
            }
        }
        catch (Exception ex)
        {
            return $"💥 Erro no processo de login: {ex.Message}";
        }
    }
}
