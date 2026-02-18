namespace Ronaldinho.Toolbox;

public static class FinancialEngine
{
    /// <summary>
    /// Calculates net present value (NPV) for a series of cash flows.
    /// </summary>
    public static double CalculateNPV(double discountRate, IEnumerable<double> cashFlows)
    {
        double npv = 0;
        int t = 0;
        foreach (var cf in cashFlows)
        {
            npv += cf / Math.Pow(1 + discountRate, t);
            t++;
        }
        return npv;
    }

    /// <summary>
    /// Estimates ROI (Return on Investment).
    /// </summary>
    public static double CalculateROI(double gainFromInvestment, double costOfInvestment)
    {
        if (costOfInvestment == 0) return 0;
        return (gainFromInvestment - costOfInvestment) / costOfInvestment;
    }

    /// <summary>
    /// Performs a simple Black-Scholes estimate for option/risk pricing (simplified).
    /// </summary>
    public static double BlackScholesCall(double s, double k, double t, double r, double v)
    {
        double d1 = (Math.Log(s / k) + (r + v * v / 2) * t) / (v * Math.Sqrt(t));
        double d2 = d1 - v * Math.Sqrt(t);
        
        // C = S*N(d1) - K*e^(-r*t)*N(d2)
        // Using approximation for Cumulative Normal Distribution
        return s * NormalDistribution(d1) - k * Math.Exp(-r * t) * NormalDistribution(d2);
    }

    private static double NormalDistribution(double d)
    {
        return 0.5 * (1 + Erf(d / Math.Sqrt(2)));
    }

    private static double Erf(double x)
    {
        // Approximation for the Error Function
        double a1 = 0.254829592;
        double a2 = -0.284496736;
        double a3 = 1.421413741;
        double a4 = -1.453152027;
        double a5 = 1.061405429;
        double p = 0.3275911;

        int sign = (x < 0) ? -1 : 1;
        x = Math.Abs(x);

        double t = 1.0 / (1.0 + p * x);
        double y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.Exp(-x * x);

        return sign * y;
    }
}
