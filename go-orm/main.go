package main

import (
	"log"
	"net/http"
	"time"

	_ "github.com/jackc/pgx/v5/stdlib"
	_ "github.com/lib/pq"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

const (
	connStr = "host=127.0.0.1 user=test password=test dbname=test port=5432 sslmode=disable"
)

var db *gorm.DB

func main() {

	http.HandleFunc("/user/", getUser)

	var err error
	db, err = gorm.Open(postgres.Open(connStr), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Error),
	})
	if err != nil {
		log.Fatalf("Failed to connect to the database: %v", err)
	}

	intDb, err := db.DB()
	if err != nil {
		log.Fatalf("Failed to fetch the connection: %v", err)
	}

	// Configure the connection pool
	intDb.SetMaxOpenConns(50)
	intDb.SetMaxIdleConns(15)
	intDb.SetConnMaxIdleTime(1 * time.Minute)
	intDb.SetConnMaxLifetime(5 * time.Minute)

	log.Fatal(http.ListenAndServe(":8080", nil))
}
