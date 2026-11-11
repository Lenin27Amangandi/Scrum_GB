
import sqlite3

DB_NAME = "reservas_epn.db"

def conectar():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS laboratorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edificio TEXT NOT NULL,
            capacidad INTEGER NOT NULL,
            equipos TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS franjas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            laboratorio_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            horario TEXT NOT NULL,
            estado TEXT DEFAULT 'DISPONIBLE',
            FOREIGN KEY (laboratorio_id)
                REFERENCES laboratorios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            laboratorio_id INTEGER NOT NULL,
            franja_id INTEGER NOT NULL,
            correo TEXT NOT NULL,
            codigo_unico TEXT NOT NULL,
            motivo TEXT NOT NULL,
            estado TEXT DEFAULT 'PENDIENTE',
            fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (laboratorio_id)
                REFERENCES laboratorios(id),
            FOREIGN KEY (franja_id)
                REFERENCES franjas(id)
        )
    """)

    conn.commit()
    conn.close()
