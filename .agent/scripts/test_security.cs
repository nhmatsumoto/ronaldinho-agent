using Ronaldinho.Toolbox;

Console.WriteLine("--- Ronaldinho Security Test ---");

string secret = "Minha chave é AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5";
string keywordSecret = "SECRET=123456";

Console.WriteLine($"Original: {secret}");
Console.WriteLine($"Sanitized: {SecurityGuard.Sanitize(secret)}");

Console.WriteLine($"Original: {keywordSecret}");
Console.WriteLine($"Sanitized: {SecurityGuard.Sanitize(keywordSecret)}");

if (SecurityGuard.ContainsSecret(secret)) {
    Console.WriteLine("SUCESSO: Segredo detectado!");
} else {
    Console.WriteLine("ERRO: Segredo não detectado.");
}
