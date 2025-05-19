import sqlite3

try:
    conn = sqlite3.connect("criminals.db", timeout=10)
    c = conn.cursor()
    c.execute("SELECT criminal_id, name, age, description, offence, status FROM criminals")
    criminals = c.fetchall()
    for criminal in criminals:
        print(f"Criminal ID: {criminal[0]}")
        print(f"Name: {criminal[1]}")
        print(f"Age: {criminal[2]}")
        print(f"Description: {criminal[3]}")
        print(f"Offence: {criminal[4]}")
        print(f"Status: {criminal[5]}")
        print("-" * 20)
    conn.close()
except Exception as e:
    print(f"Error: {str(e)}")


# try:
#     conn = sqlite3.connect("vehicles.db", timeout=10)
#     c = conn.cursor()
#     c.execute("SELECT plate_number, owner, make, model, status FROM vehicles")
#     vehicles = c.fetchall()
#     for vehicle in vehicles:
#         print(f"Plate Number: {vehicle[0]}")
#         print(f"Owner: {vehicle[1]}")
#         print(f"Make: {vehicle[2]}")
#         print(f"Model: {vehicle[3]}")
#         print(f"Status: {vehicle[4]}")
#         print("-" * 20)
#     conn.close()
# except Exception as e:
#     print(f"Error: {str(e)}")