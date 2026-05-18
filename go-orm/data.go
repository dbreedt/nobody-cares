package main

import "time"

type Data struct {
	Id     int64 `gorm:"primaryKey"`
	UserId int64
	Lat    float64
	Lon    float64
	Ts     time.Time
	Val    int64
	Value  int64
}
