namespace Ronaldinho.NeuralCore.Services;

public interface ILocalKeyVault
{
    void SaveKey(string userId, string provider, string apiKey);
    string? GetKey(string userId, string provider);
    string? GetGlobalKey(string provider);
}
