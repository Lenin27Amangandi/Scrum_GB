
from flask import Flask, render_template_string, redirect, url_for, flash
import sqlite3
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
app.secret_key = "epn_hu07_local"

CARPETA = Path(__file__).parent
BASE_DATOS = CARPETA / "reservas.db"
ARCHIVO_HTML = CARPETA / "index.html"


class ConexionBD:

    @staticmethod
    def conectar():
        conexion = sqlite3.connect(BASE_DATOS, timeout=10)
        conexion.row_factory = sqlite3.Row
        return conexion


class Solicitud:

    def __init__(
        self,
        codigo,
        estudiante,
        correo,
        laboratorio,
        fecha,
        hora_inicio,
        hora_fin,
        motivo,
        estado="Pendiente"
    ):
        self.codigo = codigo
        self.estudiante = estudiante
        self.correo = correo
        self.laboratorio = laboratorio
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.motivo = motivo
        self.estado = estado


class SolicitudRepositorio:

    @staticmethod
    def inicializar():
        conexion = ConexionBD.conectar()

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS solicitudes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                estudiante TEXT NOT NULL,
                correo TEXT NOT NULL,
                laboratorio TEXT NOT NULL,
                fecha TEXT NOT NULL,
                hora_inicio TEXT NOT NULL,
                hora_fin TEXT NOT NULL,
                motivo TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'Pendiente',
                fecha_respuesta TEXT
            )
        """)

        cantidad = conexion.execute(
            "SELECT COUNT(*) FROM solicitudes"
        ).fetchone()[0]

        if cantidad == 0:
            ejemplos = [
                (
                    "EPN-001", "Juan Pérez",
                    "juan.perez@epn.edu.ec",
                    "Laboratorio de Redes",
                    "2026-11-12", "09:00", "11:00",
                    "Práctica de configuración de redes",
                    "Pendiente", None
                ),
                (
                    "EPN-002", "María López",
                    "maria.lopez@epn.edu.ec",
                    "Laboratorio de Software",
                    "2026-11-12", "11:00", "13:00",
                    "Desarrollo de proyecto académico",
                    "Pendiente", None
                ),
                (
                    "EPN-003", "Carlos Ruiz",
                    "carlos.ruiz@epn.edu.ec",
                    "Laboratorio de Electrónica",
                    "2026-11-13", "14:00", "16:00",
                    "Práctica de circuitos electrónicos",
                    "Pendiente", None
                )
            ]

            conexion.executemany("""
                INSERT INTO solicitudes (
                    codigo, estudiante, correo, laboratorio,
                    fecha, hora_inicio, hora_fin, motivo,
                    estado, fecha_respuesta
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ejemplos)

        conexion.commit()
        conexion.close()

    @staticmethod
    def listar():
        conexion = ConexionBD.conectar()

        solicitudes = conexion.execute("""
            SELECT * FROM solicitudes
            ORDER BY id DESC
        """).fetchall()

        conexion.close()
        return solicitudes

    @staticmethod
    def obtener_por_id(id):
        conexion = ConexionBD.conectar()

        solicitud = conexion.execute("""
            SELECT * FROM solicitudes
            WHERE id = ?
        """, (id,)).fetchone()

        conexion.close()
        return solicitud

    @staticmethod
    def contar_estados():
        conexion = ConexionBD.conectar()

        estadisticas = {
            "pendiente": conexion.execute("""
                SELECT COUNT(*) FROM solicitudes
                WHERE estado = 'Pendiente'
            """).fetchone()[0],

            "aprobada": conexion.execute("""
                SELECT COUNT(*) FROM solicitudes
                WHERE estado = 'Aprobada'
            """).fetchone()[0],

            "rechazada": conexion.execute("""
                SELECT COUNT(*) FROM solicitudes
                WHERE estado = 'Rechazada'
            """).fetchone()[0]
        }

        conexion.close()
        return estadisticas


class GestionSolicitudes:

    @staticmethod
    def aprobar(id):
        conexion = ConexionBD.conectar()

        try:
            conexion.execute("BEGIN IMMEDIATE")

            solicitud = conexion.execute("""
                SELECT * FROM solicitudes
                WHERE id = ?
            """, (id,)).fetchone()

            if solicitud is None:
                conexion.rollback()
                return False, "La solicitud no existe."

            if solicitud["estado"] != "Pendiente":
                conexion.rollback()
                return False, "La solicitud ya fue procesada."

            cruce = conexion.execute("""
                SELECT id FROM solicitudes
                WHERE laboratorio = ?
                AND fecha = ?
                AND estado = 'Aprobada'
                AND hora_inicio < ?
                AND hora_fin > ?
                AND id != ?
            """, (
                solicitud["laboratorio"],
                solicitud["fecha"],
                solicitud["hora_fin"],
                solicitud["hora_inicio"],
                id
            )).fetchone()

            if cruce:
                conexion.rollback()
                return False, (
                    "Existe otra reserva aprobada "
                    "en ese horario."
                )

            conexion.execute("""
                UPDATE solicitudes
                SET estado = 'Aprobada',
                    fecha_respuesta = ?
                WHERE id = ?
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                id
            ))

            conexion.commit()
            return True, "Solicitud aprobada correctamente."

        except sqlite3.Error:
            conexion.rollback()
            return False, "Error al aprobar la solicitud."

        finally:
            conexion.close()

    @staticmethod
    def rechazar(id):
        conexion = ConexionBD.conectar()

        try:
            resultado = conexion.execute("""
                UPDATE solicitudes
                SET estado = 'Rechazada',
                    fecha_respuesta = ?
                WHERE id = ?
                AND estado = 'Pendiente'
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                id
            ))

            conexion.commit()

            if resultado.rowcount > 0:
                return True, "Solicitud rechazada correctamente."

            return False, (
                "La solicitud no existe o ya fue procesada."
            )

        except sqlite3.Error:
            conexion.rollback()
            return False, "Error al rechazar la solicitud."

        finally:
            conexion.close()


class PanelLaboratorista:

    @staticmethod
    def mostrar():
        solicitudes = SolicitudRepositorio.listar()
        estadisticas = SolicitudRepositorio.contar_estados()

        html = ARCHIVO_HTML.read_text(encoding="utf-8")

        return render_template_string(
            html,
            solicitudes=solicitudes,
            estadisticas=estadisticas
        )


@app.route("/")
def inicio():
    return PanelLaboratorista.mostrar()


@app.route("/aprobar/<int:id>", methods=["POST"])
def aprobar(id):
    exito, mensaje = GestionSolicitudes.aprobar(id)

    if exito:
        flash(mensaje, "success")
    else:
        flash(mensaje, "error")

    return redirect(url_for("inicio"))


@app.route("/rechazar/<int:id>", methods=["POST"])
def rechazar(id):
    exito, mensaje = GestionSolicitudes.rechazar(id)

    if exito:
        flash(mensaje, "success")
    else:
        flash(mensaje, "error")

    return redirect(url_for("inicio"))


if __name__ == "__main__":
    SolicitudRepositorio.inicializar()
    app.run(debug=True)
