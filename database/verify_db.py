"""
database/verify_db.py
Run this from the project root to confirm Supabase data matches schema.sql.

Usage:
    python database/verify_db.py
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

EXPECTED_PROPERTIES = 25
EXPECTED_FINANCIALS = 100

EXPECTED_COLUMNS_PROPERTIES = {
    "property_id", "address", "metro_area", "sq_footage",
    "property_type", "year_built", "occupancy_rate", "created_at"
}
EXPECTED_COLUMNS_FINANCIALS = {
    "financial_id", "property_id", "fiscal_year", "fiscal_quarter",
    "revenue", "net_income", "expenses", "created_at"
}

def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB", "postgres"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
        sslmode="require"
    )

def check(label, passed, detail=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}  {label}" + (f" — {detail}" if detail else ""))
    return passed

def main():
    print("\n=== Supabase DB Verification ===\n")

    try:
        conn = get_connection()
        print("  ✅ PASS  Connected to Supabase\n")
    except Exception as e:
        print(f"  ❌ FAIL  Could not connect: {e}")
        return

    passed = 0
    total = 0

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        # --- Row counts ---
        print("[ Row Counts ]")
        cur.execute("SELECT COUNT(*) AS n FROM properties")
        prop_count = cur.fetchone()["n"]
        total += 1; passed += check("properties row count", prop_count == EXPECTED_PROPERTIES,
                                    f"{prop_count} rows (expected {EXPECTED_PROPERTIES})")

        cur.execute("SELECT COUNT(*) AS n FROM financials")
        fin_count = cur.fetchone()["n"]
        total += 1; passed += check("financials row count", fin_count == EXPECTED_FINANCIALS,
                                    f"{fin_count} rows (expected {EXPECTED_FINANCIALS})")

        # --- Column names ---
        print("\n[ Column Names ]")
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'properties' AND table_schema = 'public'
        """)
        prop_cols = {r["column_name"] for r in cur.fetchall()}
        missing_p = EXPECTED_COLUMNS_PROPERTIES - prop_cols
        extra_p   = prop_cols - EXPECTED_COLUMNS_PROPERTIES
        total += 1; passed += check("properties columns match",
                                    not missing_p,
                                    f"missing: {missing_p}" if missing_p else "all present" + (f", extra: {extra_p}" if extra_p else ""))

        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'financials' AND table_schema = 'public'
        """)
        fin_cols = {r["column_name"] for r in cur.fetchall()}
        missing_f = EXPECTED_COLUMNS_FINANCIALS - fin_cols
        extra_f   = fin_cols - EXPECTED_COLUMNS_FINANCIALS
        total += 1; passed += check("financials columns match",
                                    not missing_f,
                                    f"missing: {missing_f}" if missing_f else "all present" + (f", extra: {extra_f}" if extra_f else ""))

        # --- FK integrity ---
        print("\n[ Foreign Key Integrity ]")
        cur.execute("""
            SELECT COUNT(*) AS n FROM financials f
            LEFT JOIN properties p ON f.property_id = p.property_id
            WHERE p.property_id IS NULL
        """)
        orphans = cur.fetchone()["n"]
        total += 1; passed += check("no orphaned financials rows", orphans == 0,
                                    f"{orphans} orphaned rows" if orphans else "all property_ids matched")

        # --- Print all rows ---
        print("\n[ Properties ]")
        cur.execute("SELECT property_id, address, metro_area, property_type, year_built, occupancy_rate FROM properties ORDER BY property_id")
        for r in cur.fetchall():
            print(f"  [{r['property_id']:>2}] {r['address'][:42]:<42} | {r['metro_area']:<15} | {r['property_type']:<12} | {r['year_built']} | occ {r['occupancy_rate']}")

        print("\n[ Financials ]")
        cur.execute("SELECT property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses FROM financials ORDER BY property_id")
        for r in cur.fetchall():
            print(f"  [{r['property_id']:>2}] FY{r['fiscal_year']} Q{r['fiscal_quarter']} | "
                  f"rev ${r['revenue']:>12,.0f} | net ${r['net_income']:>10,.0f} | exp ${r['expenses']:>10,.0f}")

    conn.close()

    print(f"\n=== Result: {passed}/{total} checks passed ===\n")

if __name__ == "__main__":
    main()
