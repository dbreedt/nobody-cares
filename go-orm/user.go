package main

import "math"

type User struct {
	Id                          uint64 `gorm:"primaryKey"`
	Name                        string
	PaymentHistoryPercentOnTime float64
	CreditUtilizationRatio      float64
	CreditAgeYears              int
	TotalAccounts               int
	RecentInquiries             int
	DerogatoryMarks             int
}

func (User) TableName() string {
	return "users"
}

func (u *User) ComputeFICO() int {
	// Payment history: 35%
	paymentScore := u.PaymentHistoryPercentOnTime * 100

	// Credit utilization: 30% (lower is better)
	utilizationScore := (1.0 - u.CreditUtilizationRatio) * 100

	// Credit age: 15% (more than 15 years is maxed)
	ageScore := math.Min(float64(u.CreditAgeYears), 15) / 15 * 100

	// Total accounts: 10% (10+ is ideal)
	accountScore := math.Min(float64(u.TotalAccounts), 10) / 10 * 100

	// Inquiries and derogatory marks: 10% (fewer is better)
	penalty := float64(u.RecentInquiries*5 + u.DerogatoryMarks*10)
	inquiryScore := math.Max(0, 100-penalty)

	// Weighted sum
	rawScore := (paymentScore * 0.35) +
		(utilizationScore * 0.30) +
		(ageScore * 0.15) +
		(accountScore * 0.10) +
		(inquiryScore * 0.10)

	// Scale to 300–850
	score := int(300 + (rawScore / 100.0 * 550))
	if score > 850 {
		score = 850
	}
	return score
}

type UserResponse struct {
	Id    uint64
	Name  string
	Score int
}

func NewUserResponse(u User) UserResponse {
	return UserResponse{
		Id:    u.Id,
		Name:  u.Name,
		Score: u.ComputeFICO(),
	}
}
