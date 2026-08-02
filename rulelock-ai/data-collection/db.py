"""
Thin PostgreSQL connection helper.
Owner: Charuka

Reads DATABASE_URL from the environment so this works identically in
Docker Compose, CI, or on someone's laptop.
"""
import os
import psycopg2


def get_connection():
    url = os.environ.get(
        "DATABASE_URL",
        "postgresql://rulelock:rulelock@localhost:5432/rulelock",
    )
    return psycopg2.connect(url)
