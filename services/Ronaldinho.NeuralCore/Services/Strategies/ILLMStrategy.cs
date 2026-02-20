using Microsoft.SemanticKernel;
using Microsoft.Extensions.Configuration;

namespace Ronaldinho.NeuralCore.Services.Strategies;

public interface ILLMStrategy
{
    string ProviderName { get; }
    void Configure(IKernelBuilder builder, IConfiguration configuration);
}
