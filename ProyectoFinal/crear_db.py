import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# BORRAR TABLA ANTIGUA
c.execute("DROP TABLE IF EXISTS coches")

# CREAR NUEVA
c.execute("""
CREATE TABLE coches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tid INTEGER,
    matricula TEXT,
    entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    salida TIMESTAMP
)
""")

conn.commit()
conn.close()

print("✅ Base de datos reiniciada correctamente")