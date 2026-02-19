using Microsoft.SemanticKernel;

namespace Ronaldinho.NeuralCore.Services.Strategies;

public interface ILLMStrategy
{
    string ProviderName { get; }
    void Configure(IKernelBuilder builder, IConfiguration configuration);
}
