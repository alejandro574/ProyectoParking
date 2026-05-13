import sqlite3
from datetime import datetime


def guardar_matricula(tid, matricula):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # =========================
    # ¿YA EXISTE ESTA MATRÍCULA ACTIVA?
    # =========================
    c.execute("""
        SELECT id
        FROM coches
        WHERE matricula = ?
        AND salida IS NULL
    """, (matricula,))

    existe = c.fetchone()

    # =========================
    # SI EXISTE -> MARCAR SALIDA
    # =========================
    if existe:

        c.execute("""
            UPDATE coches
            SET salida = CURRENT_TIMESTAMP
            WHERE matricula = ?
            AND salida IS NULL
        """, (matricula,))

        print(f"🚪 SALIDA -> {matricula}")

    # =========================
    # SI NO EXISTE -> NUEVA ENTRADA
    # =========================
    else:

        c.execute("""
            INSERT INTO coches (tid, matricula)
            VALUES (?, ?)
        """, (int(tid), matricula))

        print(f"🚘 ENTRADA -> {matricula}")

    conn.commit()
    conn.close()