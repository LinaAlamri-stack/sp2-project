import sqlite3

conn = sqlite3.connect("data/app.db")

cursor = conn.cursor()

cursor.execute("SELECT name, email FROM users")
users = cursor.fetchall()

print("\nRegistered Users:\n")

for name, email in users:
    print(f"Name: {name} | Email: {email}")

print(f"\nTotal Users: {len(users)}")

conn.close()