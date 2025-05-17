import sqlite3

try:
    conn = sqlite3.connect("criminals.db", timeout=10)
    c = conn.cursor()
    c.execute("SELECT id, name, age, description, crime, encodings FROM criminals")
    criminals = c.fetchall()
    for criminal in criminals:
        print(f"ID: {criminal[0]}")
        print(f"Name: {criminal[1]}")
        print(f"Age: {criminal[2]}")
        print(f"Description: {criminal[3]}")
        print(f"Crime: {criminal[4]}")
        print(f"Encodings: {criminal[5]}")
        print("-" * 20)
    conn.close()
except Exception as e:
    print(f"Error: {str(e)}")