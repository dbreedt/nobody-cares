export interface User {
  id: string;
  name: string;
  payment_history_percent_on_time: number;
  credit_utilization_ratio: number;
  credit_age_years: number;
  total_accounts: number;
  recent_inquiries: number;
  derogatory_marks: number;
}

export interface UserResponse {
  id: string;
  name: string;
  score: number;
}

export function toUserResponse(user: User): UserResponse {
  const paymentScore = user.payment_history_percent_on_time * 100;
  const utilizationScore = (1 - user.credit_utilization_ratio) * 100;
  const ageScore = Math.min(user.credit_age_years, 15) / 15 * 100;
  const accountScore = Math.min(user.total_accounts, 10) / 10 * 100;
  const penalty = user.recent_inquiries * 5 + user.derogatory_marks * 10;
  const inquiryScore = Math.max(0, 100 - penalty);

  const rawScore = paymentScore * 0.35 +
    utilizationScore * 0.30 +
    ageScore * 0.15 +
    accountScore * 0.10 +
    inquiryScore * 0.10;

  const fico = Math.min(850, Math.round(300 + (rawScore / 100) * 550));

  return {
    id: user.id,
    name: user.name,
    score: fico,
  };
}
