"""
database/db_client.py
PostgreSQL client for Supabase using psycopg2.
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Return a psycopg2 connection to the Supabase PostgreSQL database."""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB", "postgres"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
        sslmode="require"
    )


def get_properties(metro_area: str = None, property_type: str = None) -> list:
    """Fetch properties, optionally filtered by metro area or type."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            query = "SELECT * FROM properties WHERE 1=1"
            params = []

            if metro_area:
                query += " AND metro_area ILIKE %s"
                params.append(f"%{metro_area}%")
            if property_type:
                query += " AND property_type ILIKE %s"
                params.append(f"%{property_type}%")

            query += " LIMIT 10"
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        conn.close()


def get_property_financials(property_id: int = None) -> list:
    """Fetch property financials joined with property info."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            query = """
                SELECT f.*, p.address, p.metro_area, p.property_type
                FROM financials f
                JOIN properties p ON f.property_id = p.property_id
                WHERE 1=1
            """
            params = []

            if property_id:
                query += " AND f.property_id = %s"
                params.append(property_id)

            query += " LIMIT 10"
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        conn.close()


if __name__ == "__main__":
    print("Testing DB connection...")
    props = get_properties()
    print(f"Found {len(props)} properties")
    for p in props[:3]:
        print(f"  {p['address']} — {p['metro_area']}")
