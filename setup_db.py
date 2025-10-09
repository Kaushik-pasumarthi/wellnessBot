import sqlite3

# Create and check database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create conversations table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        user_message TEXT NOT NULL,
        bot_response TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()

# Check table
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:", tables)

# Check conversations table structure
cursor.execute("PRAGMA table_info(conversations);")
columns = cursor.fetchall()
print("Conversations table structure:", columns)

conn.close()
print("Database setup completed!")
