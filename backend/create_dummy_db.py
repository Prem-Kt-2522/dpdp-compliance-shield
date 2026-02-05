import sqlite3
import random

# Connect to (or create) the database file
conn = sqlite3.connect('vulnerable.db')
cursor = conn.cursor()

# 1. Create a "users" table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        notes TEXT
    )
''')

# 2. Insert safe dummy data
print("Injecting safe data...")
for i in range(1, 50):
    cursor.execute('INSERT INTO users (name, email, notes) VALUES (?, ?, ?)', 
                   (f"User{i}", f"user{i}@example.com", "Account verified"))

# 3. Inject DANGEROUS leaks (The stuff your scanner must find)
print("Injecting LEAKS...")
cursor.execute('INSERT INTO users (name, email, notes) VALUES (?, ?, ?)', 
               ("Amit Sharma", "amit@test.com", "Aadhaar Number: 4521 8956 2314"))

cursor.execute('INSERT INTO users (name, email, notes) VALUES (?, ?, ?)', 
               ("Sneha P", "sneha@test.com", "Phone: +91 9876543210 calls only"))

cursor.execute('INSERT INTO users (name, email, notes) VALUES (?, ?, ?)', 
               ("Rahul V", "rahul@test.com", "PAN Card ABCDE1234F verified manually"))

# Commit and close
conn.commit()
conn.close()
print("✅ 'vulnerable.db' created successfully with 3 hidden leaks.")