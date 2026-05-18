import { serve } from "https://deno.land/std/http/server.ts";
import { Pool } from "https://deno.land/x/postgres@v0.19.0/mod.ts"
import { toUserResponse, User } from "./user.ts";

const pool = new Pool("postgres://test:test@127.0.0.1:5432/test?sslmode=disable", 50, true);
const handler = async (req: Request) => {
  const url = new URL(req.url);
  const { pathname } = url;

  if (pathname.startsWith("/user/")) {
    const id = pathname.split("/")[2];
    const client = await pool.connect();
    try {
      const result = await client.queryObject<User>`
        SELECT id::int, name,
          payment_history_percent_on_time,
          credit_utilization_ratio,
          credit_age_years,
          total_accounts,
          recent_inquiries,
          derogatory_marks 
        FROM users WHERE id = ${id}
      `;

      if (result.rows.length > 0) {
        const user = result.rows[0];
        return new Response(JSON.stringify(toUserResponse(user)), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      } else {
        return new Response("User not found", { status: 404 });
      }
    } finally {
      client.release();
    }
  }

  return new Response("Not Found", { status: 404 });
};

console.log("Listening on http://0.0.0.0:8080");
await serve(handler, { port: 8080 });

