using System.ComponentModel.DataAnnotations.Schema;

namespace csorm.Models;

public class UserResponse
{
    public long Id { get; set; }
    public string Name { get; set; }
    public int Score { get; set; }

    public UserResponse(User user)
    {
        Id = user.Id;
        Name = user.Name ?? "Unknown";
        Score = CalculateScore(user);
    }

    private int CalculateScore(User u)
    {
        // Provide default values for null fields
        float paymentScore = (u.PaymentHistoryPercentOnTime ?? 0.0f) * 100f;
        float utilizationScore = Math.Max(0.0f, 1.0f - (u.CreditUtilizationRatio ?? 1.0f)) * 100f;
        float ageScore = Math.Min(u.CreditAgeYears ?? 0, 15) / 15f * 100f;
        float accountScore = Math.Min(u.TotalAccounts ?? 0, 10) / 10f * 100f;

        int inquiries = u.RecentInquiries ?? 0;
        int derog = u.DerogatoryMarks ?? 0;
        float inquiryPenalty = inquiries * 5 + derog * 10;
        float inquiryScore = Math.Max(0.0f, 100f - inquiryPenalty);

        float rawScore = paymentScore * 0.35f +
                         utilizationScore * 0.30f +
                         ageScore * 0.15f +
                         accountScore * 0.10f +
                         inquiryScore * 0.10f;

        float ficoScore = 300f + (rawScore / 100f) * 550f;
        return (int)Math.Min(Math.Round(ficoScore), 850);
    }
}