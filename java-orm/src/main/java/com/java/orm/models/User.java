package com.java.orm.models;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Entity
@Data
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    Long id;
    String name;
    @Column(name = "payment_history_percent_on_time")
    double paymentHistoryPercentOnTime;
    @Column(name = "credit_utilization_ratio")
    double creditUtilizationRatio;
    @Column(name = "credit_age_years")
    int creditAgeYears;
    @Column(name = "total_accounts")
    int totalAccounts;
    @Column(name = "recent_inquiries")
    int recentInquiries;
    @Column(name = "derogatory_marks")
    int derogatoryMarks;
}
