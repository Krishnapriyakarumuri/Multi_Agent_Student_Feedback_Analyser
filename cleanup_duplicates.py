"""
cleanup_duplicates.py
---------------------
One-time script to remove duplicate rows created by running the same CSV
multiple times before the deduplication fix was applied.

Run with:
    python cleanup_duplicates.py
"""

import sqlite3

DB_PATH = "feedback_analysis.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=== BEFORE CLEANUP ===")
for table in ["feedback", "recommendations", "sentiment_analysis", "theme_assignments", "bias_checks"]:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  {table}: {cur.fetchone()[0]} rows")

# ── Clean recommendations: keep only the oldest row per feedback_id ──────────
cur.execute("""
    DELETE FROM recommendations
    WHERE id NOT IN (
        SELECT MIN(id) FROM recommendations GROUP BY feedback_id
    )
""")
deleted_recs = cur.rowcount
print(f"\nDeleted {deleted_recs} duplicate recommendations")

# ── Clean feedback: keep only the oldest row per text_hash ───────────────────
# (only applies to rows that HAVE a text_hash)
cur.execute("""
    DELETE FROM feedback
    WHERE rowid NOT IN (
        SELECT MIN(rowid) FROM feedback GROUP BY text_hash
    )
    AND text_hash IS NOT NULL AND text_hash != ''
""")
deleted_fb = cur.rowcount
print(f"Deleted {deleted_fb} duplicate feedback rows (by text_hash)")

conn.commit()

print("\n=== AFTER CLEANUP ===")
for table in ["feedback", "recommendations", "sentiment_analysis", "theme_assignments", "bias_checks"]:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  {table}: {cur.fetchone()[0]} rows")

conn.close()
print("\n✅ Cleanup complete! Re-upload your CSV once to repopulate clean data.")
