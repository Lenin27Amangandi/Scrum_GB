
from flask import Flask, render_template, request, redirect, url_for, flash
from database import conectar, crear_tablas
import re
import uuid

app = Flask(__name__)
app.secret_key = "epn_reservas_secret"

crear_tablas()


@app.route("/")
def inicio():
    return redirect(url_for("nueva_reserva"))


@app.route("/reservar", methods=["GET", "POST"])
def nueva_reserva():

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":

        laboratorio_id = request.form.get("laboratorio_id", "").strip()
        franja_id = request.form.get("franja_id", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        codigo_unico = request.form.get("codigo_unico", "").strip()
        motivo = request.form.get("motivo", "").strip()

        # HU-04: Validar campos vacíos
        if not all([
            laboratorio_id,
            franja_id,
            correo,
            codigo_unico,
            motivo
        ]):
            flash("Todos los campos son obligatorios.", "error")

        # HU-04: Validar correo institucional
        elif not re.fullmatch(
            r"[A-Za-z0-9._%+-]+@epn\.edu\.ec",
            correo
        ):
            flash(
                "Debe ingresar un correo institucional @epn.edu.ec.",
                "error"
            )

        else:
            # Verificar que la franja exista y esté disponible
            cursor.execute("""
                SELECT * FROM franjas
                WHERE id = ?
                AND laboratorio_id = ?
                AND estado = 'DISPONIBLE'
            """, (franja_id, laboratorio_id))

            franja = cursor.fetchone()

            if not franja:
                flash(
                    "La franja seleccionada no está disponible.",
                    "error"
                )
            else:
                codigo_reserva = "EPN-2026-" + uuid.uuid4().hex[:3].upper()

                cursor.execute("""
                    INSERT INTO solicitudes (
                        codigo,
                        laboratorio_id,
                        franja_id,
                        correo,
                        codigo_unico,
                        motivo,
                        estado
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 'PENDIENTE')
                """, (
                    codigo_reserva,
                    laboratorio_id,
                    franja_id,
                    correo,
                    codigo_unico,
                    motivo
                ))

                conn.commit()

                conn.close()

                flash(
                    f"Solicitud registrada. Código: {codigo_reserva}",
                    "success"
                )

                return redirect(url_for("nueva_reserva"))

    # Obtener laboratorios para el formulario
    cursor.execute("SELECT * FROM laboratorios")
    laboratorios = cursor.fetchall()

    # Obtener franjas disponibles
    cursor.execute("""
        SELECT franjas.*, laboratorios.nombre AS laboratorio
        FROM franjas
        JOIN laboratorios
        ON franjas.laboratorio_id = laboratorios.id
        WHERE franjas.estado = 'DISPONIBLE'
    """)

    franjas = cursor.fetchall()

    conn.close()

    return render_template(
        "reserva.html",
        laboratorios=laboratorios,
        franjas=franjas
    )


if __name__ == "__main__":
    app.run(debug=True)
