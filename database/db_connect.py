import sqlite3

# Connect to database
conn = sqlite3.connect("database/youtube.db")
cursor = conn.cursor()

# Read schema.sql
with open("database/schema.sql", "r") as f:
    schema_sql = f.read()

# Execute schema
cursor.executescript(schema_sql)

# Save changes
conn.commit()

print("✅ Database connected and tables created successfully!")

# Close connection
conn.close()
