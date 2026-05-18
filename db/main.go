package main

import (
    "bufio"
    "net/http"
    "context"
    "database/sql"
    "fmt"
    "log"
    "math/rand"
    "strings"
    "time"

    "github.com/google/gofuzz"
    _ "github.com/jackc/pgx/v5/stdlib"
)

const (
    totalUsers = 500000
    batchSize  = 1000
)

type User struct {
    Name                         string
    PaymentHistoryPercentOnTime  float32
    CreditUtilizationRatio       float32
    CreditAgeYears               int
    TotalAccounts                int
    RecentInquiries              int
    DerogatoryMarks              int
}


var (
    firstNames []string
    lastNames  []string
)

func main() {
    loadNames();
    dsn := "postgres://test:test@localhost/test?sslmode=disable"
    db, err := sql.Open("pgx", dsn)
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    if err := createTable(db); err != nil {
        log.Fatal("Table creation failed:", err)
    }

    if err := seedUsers(db); err != nil {
        log.Fatal("Seeding users failed:", err)
    }

    fmt.Println("User generation complete.")
}

func createTable(db *sql.DB) error {
    query := `
    CREATE TABLE IF NOT EXISTS users (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name TEXT NOT NULL,
        payment_history_percent_on_time REAL CHECK (payment_history_percent_on_time BETWEEN 0.0 AND 1.0),
        credit_utilization_ratio REAL CHECK (credit_utilization_ratio BETWEEN 0.0 AND 1.0),
        credit_age_years INT CHECK (credit_age_years >= 0),
        total_accounts INT CHECK (total_accounts >= 0),
        recent_inquiries INT CHECK (recent_inquiries >= 0),
        derogatory_marks INT CHECK (derogatory_marks >= 0)
    );
    `
    _, err := db.Exec(query)
    return err
}

func seedUsers(db *sql.DB) error {
    rand.Seed(time.Now().UnixNano())
    ctx := context.Background()

    f := fuzz.New().NilChance(0).Funcs(
        func(u *User, c fuzz.Continue) {
            u.Name = randomName()
            u.PaymentHistoryPercentOnTime = clamp(rand.NormFloat64()*0.05+0.95, 0.7, 1.0)
            u.CreditUtilizationRatio = clamp(rand.NormFloat64()*0.1+0.35, 0.0, 1.0)
            u.CreditAgeYears = rand.Intn(25)
            u.TotalAccounts = rand.Intn(15) + 1
            u.RecentInquiries = weightedRandom([]int{0, 1, 2, 3, 4}, []int{50, 30, 10, 7, 3})
            u.DerogatoryMarks = weightedRandom([]int{0, 1, 2}, []int{90, 8, 2})
        },
    )

    for i := 0; i < totalUsers; i += batchSize {
        var builder strings.Builder
        builder.WriteString("INSERT INTO users (name, payment_history_percent_on_time, credit_utilization_ratio, credit_age_years, total_accounts, recent_inquiries, derogatory_marks) VALUES ")

        vals := []any{}
        for j := 0; j < batchSize && i+j < totalUsers; j++ {
            if j > 0 {
                builder.WriteString(", ")
            }

            var user User
            f.Fuzz(&user)

            builder.WriteString(fmt.Sprintf("($%d,$%d,$%d,$%d,$%d,$%d,$%d)",
                j*7+1, j*7+2, j*7+3, j*7+4, j*7+5, j*7+6, j*7+7))
            vals = append(vals, user.Name, user.PaymentHistoryPercentOnTime, user.CreditUtilizationRatio, user.CreditAgeYears, user.TotalAccounts, user.RecentInquiries, user.DerogatoryMarks)
        }

        _, err := db.ExecContext(ctx, builder.String(), vals...)
        if err != nil {
            return err
        }

        if (i+batchSize)%10000 == 0 {
            log.Printf("Inserted %d users...", i+batchSize)
        }
    }

    return nil
}

func clamp(val float64, min float64, max float64) float32 {
    if val < min {
        return float32(min)
    }
    if val > max {
        return float32(max)
    }
    return float32(val)
}

func weightedRandom(values []int, weights []int) int {
    total := 0
    for _, w := range weights {
        total += w
    }

    r := rand.Intn(total)
    for i, w := range weights {
        if r < w {
            return values[i]
        }
        r -= w
    }

    return values[0]
}

func init() {
    rand.Seed(time.Now().UnixNano())
    loadNames()
}

func loadNames() {
    var err error
    firstNames, err = fetchNameList("https://raw.githubusercontent.com/dominictarr/random-name/master/first-names.txt")
    if err != nil {
        log.Fatalf("failed to fetch first names: %v", err)
    }

    lastNames, err = fetchNameList("https://raw.githubusercontent.com/dominictarr/random-name/master/names.txt")
    if err != nil {
        log.Fatalf("failed to fetch last names: %v", err)
    }

    log.Printf("Loaded %d first names and %d last names", len(firstNames), len(lastNames))
}

func fetchNameList(url string) ([]string, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    scanner := bufio.NewScanner(resp.Body)
    var names []string
    for scanner.Scan() {
        line := strings.TrimSpace(scanner.Text())
        if line != "" {
            names = append(names, strings.Title(line))
        }
    }
    return names, scanner.Err()
}

func randomName() string {
    first := firstNames[rand.Intn(len(firstNames))]
    last := lastNames[rand.Intn(len(lastNames))]
    return fmt.Sprintf("%s %s", first, last)
}
