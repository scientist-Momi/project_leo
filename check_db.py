import sqlite3

try:
    conn = sqlite3.connect("criminals.db", timeout=10)
    c = conn.cursor()
    c.execute("SELECT name, age, description, offence, status FROM criminals")
    criminals = c.fetchall()
    for criminal in criminals:
        print(f"Name: {criminal[0]}")
        print(f"Age: {criminal[1]}")
        print(f"Description: {criminal[2]}")
        print(f"Offence: {criminal[3]}")
        print(f"Status: {criminal[4]}")
        print("-" * 20)
    conn.close()
except Exception as e:
    print(f"Error: {str(e)}")