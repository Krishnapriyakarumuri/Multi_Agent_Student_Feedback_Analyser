import sqlite3

conn = sqlite3.connect("feedback_analysis.db")
cur = conn.cursor()

# Check if feedback_ids are actually unique in recommendations
cur.execute("SELECT COUNT(*) FROM recommendations")
total = cur.fetchone()[0]

cur.execute("SELECT COUNT(DISTINCT feedback_id) FROM recommendations")
unique_fids = cur.fetchone()[0]

print(f"Total recommendations: {total}")
print(f"Unique feedback_ids:   {unique_fids}")

# Check if text_hash is populated in feedback table
cur.execute("SELECT COUNT(*) FROM feedback WHERE text_hash IS NULL OR text_hash = ''")
no_hash = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM feedback")
total_fb = cur.fetchone()[0]
print(f"\nFeedback rows with empty text_hash: {no_hash} / {total_fb}")

# Sample a few feedback rows
cur.execute("SELECT id, text_hash FROM feedback LIMIT 5")
print("\nSample feedback rows (id, text_hash):")
for r in cur.fetchall():
    print(f"  id={r[0][:35]}  hash={str(r[1])[:20]}")

# Sample a few recommendation rows
cur.execute("SELECT feedback_id, recommendation_text FROM recommendations LIMIT 3")
print("\nSample recommendations:")
for r in cur.fetchall():
    print(f"  fid={r[0][:35]}  rec={r[1][:50]}")

# Check if same original_text appears multiple times in feedback
cur.execute("""
    SELECT original_text, COUNT(*) as cnt
    FROM feedback
    GROUP BY original_text
    HAVING cnt > 1
    LIMIT 5
""")
dupe_texts = cur.fetchall()
print(f"\nFeedback texts appearing more than once: {len(dupe_texts)}")
for r in dupe_texts:
    print(f"  cnt={r[1]}  text={r[0][:70]}")

# Check duplicate recommendations by recommendation_text
cur.execute("""
    SELECT recommendation_text, COUNT(*) as cnt
    FROM recommendations
    GROUP BY recommendation_text
    HAVING cnt > 1
    LIMIT 5
""")
dupe_recs = cur.fetchall()
print(f"\nRecommendation texts appearing more than once: {len(dupe_recs)}")
for r in dupe_recs:
    print(f"  cnt={r[1]}  text={r[0][:70]}")

conn.close()
