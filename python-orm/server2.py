# /// script
# dependencies = [
#   "fastapi",
#   "uvicorn",
#   "psycopg[pool]",
#   "granian"
# ]
# ///
import os
import math
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row

# --- Types & Logic (Equivalent to user.ts) ---

class User(BaseModel):
    id: int
    name: str
    payment_history_percent_on_time: float
    credit_utilization_ratio: float
    credit_age_years: int
    total_accounts: int
    recent_inquiries: int
    derogatory_marks: int

class UserResponse(BaseModel):
    id: str
    name: str
    score: int

def to_user_response(user: dict) -> UserResponse:
    # Logic ported from your TypeScript toUserResponse
    payment_score = user["payment_history_percent_on_time"] * 100
    utilization_score = (1 - user["credit_utilization_ratio"]) * 100
    age_score = min(user["credit_age_years"], 15) / 15 * 100
    account_score = min(user["total_accounts"], 10) / 10 * 100
    penalty = user["recent_inquiries"] * 5 + user["derogatory_marks"] * 10
    inquiry_score = max(0, 100 - penalty)

    raw_score = (
        payment_score * 0.35 +
        utilization_score * 0.30 +
        age_score * 0.15 +
        account_score * 0.10 +
        inquiry_score * 0.10
    )

    fico = min(850, round(300 + (raw_score / 100) * 550))
    
    return UserResponse(
        id=str(user["id"]),
        name=user["name"],
        score=fico
    )

# --- Server Setup (Equivalent to server.ts) ---

DATABASE_URL = "postgres://test:test@127.0.0.1:5432/test"

# Use a connection pool similar to Deno's Pool
pool = AsyncConnectionPool(conninfo=DATABASE_URL, min_size=15, max_size=50, open=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Open the pool
    await pool.open()
    yield
    # Shutdown: Close the pool
    await pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/user/{user_id}")
async def get_user(user_id: int):
    async with pool.connection() as conn:
        # dict_row makes the result behave like the Deno queryObject
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT id::int, name,
                  payment_history_percent_on_time,
                  credit_utilization_ratio,
                  credit_age_years,
                  total_accounts,
                  recent_inquiries,
                  derogatory_marks 
                FROM users WHERE id = %s
                """,
                (user_id,)
            )
            user = await cur.fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return to_user_response(user)

if __name__ == "__main__":
    import uvicorn
    print("Listening on http://0.0.0.0:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080, access_log=False)
