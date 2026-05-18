using System.ComponentModel.DataAnnotations.Schema;

namespace csorm.Models;

[Table("users")]
public class User
{
    [Column("id")]
    public long Id { get; set; }
    [Column("name")]
    public string? Name { get; set; }
    [Column("payment_history_percent_on_time")]
    public float? PaymentHistoryPercentOnTime { get; set; }
    [Column("credit_utilization_ratio")]
    public float? CreditUtilizationRatio { get; set; }
    [Column("credit_age_years")]
    public int? CreditAgeYears { get; set; }
    [Column("total_accounts")]
    public int? TotalAccounts { get; set; }
    [Column("recent_inquiries")]
    public int? RecentInquiries { get; set; }
    [Column("derogatory_marks")]
    public int? DerogatoryMarks { get; set; }
}