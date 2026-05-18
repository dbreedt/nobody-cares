package com.java.orm.models;

import lombok.Data;

@Data
public class UserResponse {
    private long id;
    private String name;
    private int score;

    public UserResponse(User u) {
        this.id = u.getId();
        this.name = u.getName();
        this.score = calculateFicoScore(u);
    }

    private int calculateFicoScore(User u) {
        double paymentScore = u.paymentHistoryPercentOnTime * 100.0;
        double utilizationScore = Math.max(0.0, 1.0 - u.creditUtilizationRatio) * 100.0;
        double ageScore = Math.min(u.creditAgeYears, 15) / 15.0 * 100.0;
        double accountScore = Math.min(u.totalAccounts, 10) / 10.0 * 100.0;

        double inquiryPenalty = u.recentInquiries * 5.0 + u.derogatoryMarks * 10.0;
        double inquiryScore = Math.max(0.0, 100.0 - inquiryPenalty);

        double rawScore = paymentScore * 0.35 +
                utilizationScore * 0.30 +
                ageScore * 0.15 +
                accountScore * 0.10 +
                inquiryScore * 0.10;

        double fico = 300.0 + (rawScore / 100.0) * 550.0;
        return Math.min((int) Math.round(fico), 850);
    }
}
