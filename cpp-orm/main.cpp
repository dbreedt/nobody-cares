#include <drogon/drogon.h>
#include <cmath>
#include <algorithm>

using namespace drogon;
using namespace drogon::orm;

Json::Value calculateScore(const Row &row) {
    auto payment_history = row["payment_history_percent_on_time"].as<float>();
    auto utilization_ratio = row["credit_utilization_ratio"].as<float>();
    auto age_years = row["credit_age_years"].as<int>();
    auto total_accounts = row["total_accounts"].as<int>();
    auto recent_inquiries = row["recent_inquiries"].as<int>();
    auto derogatory_marks = row["derogatory_marks"].as<int>();

    double payment_score = payment_history * 100.0;
    double utilization_score = (1.0 - utilization_ratio) * 100.0;
    double age_score = (std::min(age_years, 15) / 15.0) * 100.0;
    double account_score = (std::min(total_accounts, 10) / 10.0) * 100.0;
    
    int penalty = (recent_inquiries * 5) + (derogatory_marks * 10);
    double inquiry_score = std::max(0, 100 - penalty);

    double raw_score = (payment_score * 0.35) +
                       (utilization_score * 0.30) +
                       (age_score * 0.15) +
                       (account_score * 0.10) +
                       (inquiry_score * 0.10);

    int fico = std::min(850, (int)std::round(300 + (raw_score / 100.0) * 550));

    Json::Value ret;
    ret["id"] = std::to_string(row["id"].as<int64_t>());
    ret["name"] = row["name"].as<std::string>();
    ret["score"] = fico;
    return ret;
}

int main() {
    app().addListener("0.0.0.0", 8080);
    
    app().createDbClient("postgresql", "127.0.0.1", 5432, "test", "test", "test", 50);

    app().registerHandler("/user/{id}", 
        [](const HttpRequestPtr& req, 
           std::function<void (const HttpResponsePtr &)> &&callback, 
           long long userId) 
    {
        auto dbClient = app().getDbClient();
        dbClient->execSqlAsync(
            "SELECT id, name, payment_history_percent_on_time, credit_utilization_ratio, "
            "credit_age_years, total_accounts, recent_inquiries, derogatory_marks "
            "FROM users WHERE id = $1",
            [callback](const Result &r) {
                if (r.empty()) {
                    auto resp = HttpResponse::newHttpResponse(k404NotFound, CT_TEXT_PLAIN);
                    callback(resp);
                    return;
                }
                auto json = calculateScore(r[0]);
                auto resp = HttpResponse::newHttpJsonResponse(json);
                callback(resp);
            },
            [callback](const DrogonDbException &e) {
                auto resp = HttpResponse::newHttpResponse(k500InternalServerError, CT_TEXT_PLAIN);
                callback(resp);
            },
            userId
        );
    }, {Get});

    LOG_INFO << "Server listening on 0.0.0.0:8080";
    app().run();
    return 0;
}
