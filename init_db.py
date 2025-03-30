import sqlite3

DB_NAME = 'database.db'

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Táblák létrehozása
cursor.execute('''
    CREATE TABLE IF NOT EXISTS keszlet (
        ceg TEXT PRIMARY KEY,
        liter REAL NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tankolas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datum TEXT NOT NULL,
        gep_neve TEXT NOT NULL,
        uzemora INTEGER NOT NULL,
        liter REAL NOT NULL,
        gepkezelo TEXT NOT NULL,
        sofor TEXT NOT NULL
    )
''')

# Mintaadatok feltöltése (csak ha üres)
cursor.execute("SELECT COUNT(*) FROM keszlet")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO keszlet (ceg, liter) VALUES (?, ?)", ("Doka Hungary", 300.0))
    cursor.execute("INSERT INTO keszlet (ceg, liter) VALUES (?, ?)", ("Acél Kft.", 250.0))

conn.commit()
conn.close()

print("Adatbázis inicializálva.")
