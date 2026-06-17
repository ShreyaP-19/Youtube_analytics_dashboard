import sqlite3

conn = sqlite3.connect("database/youtube.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE videos ADD COLUMN views INTEGER")
cursor.execute("ALTER TABLE videos ADD COLUMN likes INTEGER")
cursor.execute("ALTER TABLE videos ADD COLUMN comments INTEGER")
cursor.execute("ALTER TABLE videos ADD COLUMN engagement_rate REAL")

conn.commit()
conn.close()

print("Columns added successfully")