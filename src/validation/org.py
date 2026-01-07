import sqlite3

conn = sqlite3.connect(
    r"/home/user/Desktop/output/output/asana_simulation.sqlite"
)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM organizations;")
print("Total rows:", cursor.fetchone()[0])

cursor.execute("SELECT * FROM organizations LIMIT 5;")
for row in cursor.fetchall():
    print(row)


cursor.execute("SELECT * FROM organizations where name == 'DoorDash';")
for row in cursor.fetchall():
    print(row)

conn.close()
