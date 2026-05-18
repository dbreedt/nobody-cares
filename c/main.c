#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/tcp.h>
#include <libpq-fe.h>
#include <math.h>
#include <sys/wait.h>
#include <endian.h>

#define PORT 8080
#define CONCURRENCY 5 

// Fast binary data conversion
static inline float pq_get_float(const char *ptr) {
    uint32_t net;
    memcpy(&net, ptr, 4);
    net = be32toh(net);
    float val;
    memcpy(&val, &net, 4);
    return val;
}

static inline int pq_get_int(const char *ptr) {
    uint32_t net;
    memcpy(&net, ptr, 4);
    return (int)be32toh(net);
}

void handle_client(int client_socket, PGconn *conn) {
    char buffer[2048];
    
    // KEEP-ALIVE LOOP: Keep the socket open until the client hangs up
    while (1) {
        ssize_t n = read(client_socket, buffer, sizeof(buffer));
        if (n <= 0) break; 

        char *id_ptr = strstr(buffer, "/user/");
        if (!id_ptr) break;

        char id_str[16] = {0};
        sscanf(id_ptr + 6, "%15s", id_str);

        const char *params[1] = {id_str};
        // resultFormat = 1 (Binary)
        PGresult *res = PQexecPrepared(conn, "get_user", 1, params, NULL, NULL, 1);

        if (PQresultStatus(res) == PGRES_TUPLES_OK && PQntuples(res) > 0) {
            float p_hist = pq_get_float(PQgetvalue(res, 0, 2));
            float u_rat  = pq_get_float(PQgetvalue(res, 0, 3));
            int age      = pq_get_int(PQgetvalue(res, 0, 4));
            int accs     = pq_get_int(PQgetvalue(res, 0, 5));
            int inq      = pq_get_int(PQgetvalue(res, 0, 6));
            int der      = pq_get_int(PQgetvalue(res, 0, 7));

            double raw = (p_hist * 35.0) + ((1.0 - u_rat) * 30.0) +
                         ((fmin(age, 15) / 15.0) * 15.0) + 
                         ((fmin(accs, 10) / 10.0) * 10.0) +
                         (fmax(0, 100 - (inq * 5 + der * 10)) * 0.10);
            
            int fico = (int)round(300 + (raw / 100.0) * 550);
            if (fico > 850) fico = 850;

            char body[256];
            int b_len = sprintf(body, "{\"id\":\"%s\",\"name\":\"%s\",\"score\":%d}", 
                                PQgetvalue(res, 0, 0), PQgetvalue(res, 0, 1), fico);
            
            char full_res[1024];
            int total = sprintf(full_res, 
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n"
                "Content-Length: %d\r\n"
                "Connection: keep-alive\r\n\r\n%s", b_len, body);
            
            if (write(client_socket, full_res, total) < 0) break;
        }
        PQclear(res);
    }
    close(client_socket);
}

int main() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));

    struct sockaddr_in addr = {.sin_family = AF_INET, .sin_addr.s_addr = INADDR_ANY, .sin_port = htons(PORT)};
    bind(server_fd, (struct sockaddr *)&addr, sizeof(addr));
    listen(server_fd, 1024);

    for (int i = 0; i < CONCURRENCY; i++) {
        if (fork() == 0) {
            // PRO-TIP: Try host=/var/run/postgresql to bypass TCP for Postgres
            PGconn *conn = PQconnectdb("host=127.0.0.1 port=5432 dbname=test user=test password=test");
            
            PQprepare(conn, "get_user", 
                "SELECT id, name, payment_history_percent_on_time, credit_utilization_ratio, "
                "credit_age_years, total_accounts, recent_inquiries, derogatory_marks "
                "FROM users WHERE id = $1", 1, NULL);

            while (1) {
                int client_socket = accept(server_fd, NULL, NULL);
                if (client_socket >= 0) {
                    setsockopt(client_socket, IPPROTO_TCP, TCP_NODELAY, &opt, sizeof(opt));
                    handle_client(client_socket, conn);
                }
            }
            PQfinish(conn);
            exit(0);
        }
    }
    while(wait(NULL) > 0);
    return 0;
}