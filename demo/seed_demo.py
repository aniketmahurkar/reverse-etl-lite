#!/usr/bin/env python3
"""Seed a demo SQLite database simulating dbt model output."""
import sqlite3
import random
from pathlib import Path

DB_PATH = Path(__file__).parent / "demo.db"

SEGMENTS = ["enterprise", "mid-market", "smb"]
RISKS = ["low", "medium", "high"]


def seed():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE customer_health_scores (
            customer_id TEXT PRIMARY KEY,
            company_name TEXT,
            health_score INTEGER,
            segment TEXT,
            last_contact_date TEXT,
            mrr REAL,
            churn_risk TEXT
        )
    """)

    for i in range(50):
        conn.execute(
            "INSERT INTO customer_health_scores VALUES (?,?,?,?,?,?,?)",
            (
                f"cust_{i:04d}",
                f"Company {chr(65 + i % 26)}{i}",
                random.randint(20, 100),
                random.choice(SEGMENTS),
                f"2026-05-{random.randint(1, 17):02d}",
                round(random.uniform(500, 50000), 2),
                random.choice(RISKS),
            ),
        )

    conn.commit()
    conn.close()
    print(f"Demo database created at {DB_PATH} (50 customers)")


if __name__ == "__main__":
    seed()
