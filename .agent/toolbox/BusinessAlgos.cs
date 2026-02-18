namespace Ronaldinho.Toolbox;

public static class BusinessAlgos
{
    /// <summary>
    /// Performs a simple Monte Carlo simulation for project profitability risk.
    /// </summary>
    public static (double AvgProfit, double ProbabilityOfLoss) MonteCarloProfitRisk(double baseProfit, double volatility, int iterations = 1000)
    {
        var random = new Random();
        var results = new List<double>();
        int losses = 0;

        for (int i = 0; i < iterations; i++)
        {
            // Simple normal distribution simulation (approx)
            double u1 = 1.0 - random.NextDouble();
            double u2 = 1.0 - random.NextDouble();
            double randStdNormal = Math.Sqrt(-2.0 * Math.Log(u1)) * Math.Sin(2.0 * Math.PI * u2);
            
            double simulatedProfit = baseProfit + (volatility * baseProfit * randStdNormal);
            results.Add(simulatedProfit);
            if (simulatedProfit < 0) losses++;
        }

        return (results.Average(), (double)losses / iterations);
    }

    /// <summary>
    /// Calculates Unit Economics metrics (CAC, LTV, Margin).
    /// </summary>
    public static double CalculateLTV(double arpu, double churnRate, double marginPercent)
    {
        if (churnRate <= 0) return double.PositiveInfinity;
        return (arpu * marginPercent) / churnRate;
    }
}
