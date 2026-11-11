import sqlite3
from datetime import datetime

from flask import Flask, render_template, request

app = Flask(__name__)
DATABASE = "reservas.db"


def conectar():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tabla():
    with conectar() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                fecha TEXT NOT NULL,
                hora_inicio TEXT NOT NULL,
                hora_fin TEXT NOT NULL,
                laboratorio TEXT NOT NULL
            )
            """
        )


def obtener_reservas():
    with conectar() as conexion:
        return conexion.execute(
            """
            SELECT nombre, fecha, hora_inicio, hora_fin, laboratorio
            FROM reservas
            ORDER BY fecha, hora_inicio, laboratorio
            """
        ).fetchall()


@app.route("/", methods=["GET", "POST"])
def inicio():
    mensaje = ""
    tipo_mensaje = ""

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        fecha = request.form.get("fecha", "")
        hora_inicio = request.form.get("hora_inicio", "")
        hora_fin = request.form.get("hora_fin", "")
        laboratorio = request.form.get("laboratorio", "").strip()

        try:
            inicio = datetime.strptime(hora_inicio, "%H:%M")
            fin = datetime.strptime(hora_fin, "%H:%M")
        except ValueError:
            mensaje = "Selecciona una hora de inicio y una hora de fin válidas."
            tipo_mensaje = "error"
        else:
            if not all([nombre, fecha, laboratorio]):
                mensaje = "Completa todos los campos."
                tipo_mensaje = "error"
            elif inicio >= fin:
                mensaje = "La hora de fin debe ser posterior a la hora de inicio."
                tipo_mensaje = "error"
            else:
                with sqlite3.connect(DATABASE, isolation_level="IMMEDIATE") as conexion:
                    cruce = conexion.execute(
                        """
                        SELECT 1
                        FROM reservas
                        WHERE fecha = ?
                          AND laboratorio = ?
                          AND hora_inicio < ?
                          AND hora_fin > ?
                        LIMIT 1
                        """,
                        (fecha, laboratorio, hora_fin, hora_inicio),
                    ).fetchone()

                    if cruce:
                        mensaje = (
                            "No se puede reservar: el laboratorio ya está "
                            "ocupado en esa franja."
                        )
                        tipo_mensaje = "error"
                    else:
                        conexion.execute(
                            """
                            INSERT INTO reservas
                            (nombre, fecha, hora_inicio, hora_fin, laboratorio)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (nombre, fecha, hora_inicio, hora_fin, laboratorio),
                        )
                        mensaje = "Reserva confirmada. La franja ha sido bloqueada."
                        tipo_mensaje = "exito"

    return render_template(
        "index.html",
        mensaje=mensaje,
        tipo_mensaje=tipo_mensaje,
        reservas=obtener_reservas(),
    )


crear_tabla()


if __name__ == "__main__":
    app.run(debug=True)
