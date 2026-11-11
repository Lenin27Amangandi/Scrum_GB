import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, jsonify, abort
from backend.repositorio import listar_laboratorios
from pathlib import Path
import re
import os

app = Flask(__name__)
DATABASE = os.environ.get("RESERVAS_DATABASE", str(Path(__file__).with_name("reservas.db")))


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

    laboratorios = listar_laboratorios()
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        fecha = request.form.get("fecha", "")
        hora_inicio = request.form.get("hora_inicio", "")
        hora_fin = request.form.get("hora_fin", "")
        laboratorio = request.form.get("laboratorio", "").strip()

        correo = request.form.get("correo", "").strip().lower()
        codigo_unico = request.form.get("codigo_unico", "").strip()
        motivo = request.form.get("motivo", "").strip()
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
            inicio = datetime.strptime(hora_inicio, "%H:%M")
            fin = datetime.strptime(hora_fin, "%H:%M")
        except ValueError:
            mensaje = "Selecciona una hora de inicio y una hora de fin válidas."
            tipo_mensaje = "error"
        else:
            if laboratorio not in {lab["id"] for lab in laboratorios}:
                mensaje = "Selecciona un laboratorio del catálogo."
                tipo_mensaje = "error"
            elif not re.fullmatch(r"[A-Za-z0-9._%+-]+@epn\.edu\.ec", correo) or not codigo_unico or not motivo:
                mensaje = "Completa código, motivo y correo institucional @epn.edu.ec."
                tipo_mensaje = "error"
            elif not all([nombre, fecha, laboratorio]):
                mensaje = "Completa todos los campos."
                tipo_mensaje = "error"
            elif inicio >= fin:
                mensaje = "La hora de fin debe ser posterior a la hora de inicio."
                tipo_mensaje = "error"
            else:
                with sqlite3.connect(DATABASE, isolation_level="IMMEDIATE") as conexion:
                    conexion.execute("BEGIN IMMEDIATE")
                    mantenimiento = conexion.execute("SELECT 1 FROM mantenimientos WHERE fecha=? AND laboratorio=? AND hora_inicio < ? AND hora_fin > ?", (fecha, laboratorio, hora_fin, hora_inicio)).fetchone()
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

                    if cruce or mantenimiento:
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
                        reserva_id = conexion.execute("SELECT last_insert_rowid()").fetchone()[0]
                        conexion.execute("INSERT INTO detalles_reserva (reserva_id, correo, codigo_unico, motivo) VALUES (?, ?, ?, ?)", (reserva_id, correo, codigo_unico, motivo))
                        conexion.commit()
                        return render_template("comprobante.html", reserva={"id": reserva_id, "nombre": nombre, "correo": correo, "laboratorio": laboratorio, "fecha": fecha, "hora_inicio": hora_inicio, "hora_fin": hora_fin, "motivo": motivo})
                        tipo_mensaje = "exito"

    return render_template(
        "index.html",
        mensaje=mensaje,
        tipo_mensaje=tipo_mensaje,
        reservas=obtener_reservas(),
        laboratorios=laboratorios,
    )


crear_tabla()
with conectar() as conexion:
    conexion.execute("CREATE TABLE IF NOT EXISTS mantenimientos (id INTEGER PRIMARY KEY, laboratorio TEXT NOT NULL, fecha TEXT NOT NULL, hora_inicio TEXT NOT NULL, hora_fin TEXT NOT NULL)")
    conexion.execute("CREATE TABLE IF NOT EXISTS detalles_reserva (reserva_id INTEGER PRIMARY KEY, correo TEXT, codigo_unico TEXT, motivo TEXT)")

@app.get('/api/laboratorios')
def catalogo_api():
    return jsonify(listar_laboratorios())

@app.get('/api/franjas')
def franjas_api():
    laboratorio = request.args.get('laboratorio', '')
    fecha = request.args.get('fecha', '')
    if laboratorio not in {lab['id'] for lab in listar_laboratorios()}:
        abort(400)
    try:
        datetime.strptime(fecha, '%Y-%m-%d')
    except ValueError:
        abort(400)
    franjas = []
    with conectar() as conexion:
        for inicio, fin in [('07:00', '09:00'), ('09:00', '11:00'), ('11:00', '13:00'), ('14:00', '16:00')]:
            params = (fecha, laboratorio, fin, inicio)
            mantenimiento = conexion.execute('SELECT 1 FROM mantenimientos WHERE fecha=? AND laboratorio=? AND hora_inicio < ? AND hora_fin > ?', params).fetchone()
            ocupada = conexion.execute('SELECT 1 FROM reservas WHERE fecha=? AND laboratorio=? AND hora_inicio < ? AND hora_fin > ?', params).fetchone()
            franjas.append({'time': f'{inicio} – {fin}', 'state': 'mantenimiento' if mantenimiento else 'ocupado' if ocupada else 'disponible'})
    return jsonify(franjas)

if __name__ == "__main__":
    app.run(debug=True)
