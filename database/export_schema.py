"""
database/export_schema.py
Connects to Supabase and regenerates schema.sql with the exact data that
is currently in the database — so the file is always apples-to-apples.

Usage:
    python database/export_schema.py
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

OUTPUT = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB", "postgres"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
        sslmode="require"
    )


def main():
    print("Connecting to Supabase...")
    conn = get_connection()
    print("Connected.\n")

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        # --- Fetch all properties ---
        cur.execute("SELECT * FROM properties ORDER BY property_id")
        properties = cur.fetchall()

        # --- Fetch all financials ---
        cur.execute("SELECT * FROM financials ORDER BY property_id, fiscal_year, fiscal_quarter")
        financials = cur.fetchall()

    conn.close()

    print(f"Found {len(properties)} properties and {len(financials)} financial records.")
    print(f"Writing to {OUTPUT} ...")

    lines = []
    lines.append("-- =============================================================================")
    lines.append("-- schema.sql")
    lines.append("-- Supabase (PostgreSQL) schema for the Realty Income Financial Assistant")
    lines.append("-- Auto-generated from live Supabase data via export_schema.py")
    lines.append("-- Run these statements in the Supabase SQL Editor to recreate the database.")
    lines.append("-- =============================================================================")
    lines.append("")

    # --- CREATE TABLE: properties ---
    lines.append("-- -----------------------------------------------------------------------------")
    lines.append("-- Properties table")
    lines.append("-- -----------------------------------------------------------------------------")
    lines.append("CREATE TABLE IF NOT EXISTS properties (")
    lines.append("    property_id    SERIAL PRIMARY KEY,")
    lines.append("    address        VARCHAR NOT NULL,")
    lines.append("    metro_area     VARCHAR NOT NULL,")
    lines.append("    sq_footage     INTEGER,")
    lines.append("    property_type  VARCHAR NOT NULL,")
    lines.append("    year_built     INTEGER,")
    lines.append("    occupancy_rate NUMERIC,")
    lines.append("    created_at     TIMESTAMP DEFAULT NOW()")
    lines.append(");")
    lines.append("")

    # --- CREATE TABLE: financials ---
    lines.append("-- -----------------------------------------------------------------------------")
    lines.append("-- Financials table")
    lines.append("-- -----------------------------------------------------------------------------")
    lines.append("CREATE TABLE IF NOT EXISTS financials (")
    lines.append("    financial_id   SERIAL PRIMARY KEY,")
    lines.append("    property_id    INTEGER NOT NULL REFERENCES properties(property_id),")
    lines.append("    fiscal_year    INTEGER,")
    lines.append("    fiscal_quarter INTEGER,")
    lines.append("    revenue        NUMERIC,")
    lines.append("    net_income     NUMERIC,")
    lines.append("    expenses       NUMERIC,")
    lines.append("    created_at     TIMESTAMP DEFAULT NOW()")
    lines.append(");")
    lines.append("")

    # --- INSERT: properties ---
    lines.append("-- -----------------------------------------------------------------------------")
    lines.append(f"-- Seed data: {len(properties)} properties")
    lines.append("-- -----------------------------------------------------------------------------")
    for p in properties:
        addr  = str(p["address"]).replace("'", "''")
        metro = str(p["metro_area"]).replace("'", "''")
        ptype = str(p["property_type"]).replace("'", "''")
        sqft  = p["sq_footage"] if p["sq_footage"] is not None else "NULL"
        yb    = p["year_built"] if p["year_built"] is not None else "NULL"
        occ   = p["occupancy_rate"] if p["occupancy_rate"] is not None else "NULL"
        lines.append(
            f"INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) "
            f"VALUES ({p['property_id']}, '{addr}', '{metro}', {sqft}, '{ptype}', {yb}, {occ});"
        )

    lines.append("")

    # --- INSERT: financials ---
    lines.append("-- -----------------------------------------------------------------------------")
    lines.append(f"-- Seed data: {len(financials)} financial records ({len(financials) // len(properties)} quarters per property)")
    lines.append("-- -----------------------------------------------------------------------------")
    for f in financials:
        rev = f["revenue"]    if f["revenue"]    is not None else "NULL"
        net = f["net_income"] if f["net_income"] is not None else "NULL"
        exp = f["expenses"]   if f["expenses"]   is not None else "NULL"
        fy  = f["fiscal_year"]    if f["fiscal_year"]    is not None else "NULL"
        fq  = f["fiscal_quarter"] if f["fiscal_quarter"] is not None else "NULL"
        lines.append(
            f"INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) "
            f"VALUES ({f['financial_id']}, {f['property_id']}, {fy}, {fq}, {rev}, {net}, {exp});"
        )

    lines.append("")

    with open(OUTPUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print(f"Done! schema.sql updated with {len(properties)} properties and {len(financials)} financials.")
    print("Commit this file to GitHub and it will always match Supabase exactly.")


if __name__ == "__main__":
    main()
