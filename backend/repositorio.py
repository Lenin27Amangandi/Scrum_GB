"""Acceso a datos de laboratorios almacenados en CSV (HU-01)."""

import csv
from pathlib import Path

CSV_LABORATORIOS = Path(__file__).parent / "data" / "laboratorios.csv"


def _parsear_equipos(texto):
    """Convierte 'Equipo A:3;Equipo B:5' en [{'nombre': 'Equipo A', 'cantidad': 3}, ...]."""
    equipos = []
    for item in (texto or "").split(";"):
        item = item.strip()
        if not item:
            continue
        nombre, _, cantidad = item.rpartition(":")
        if not nombre:  # Sin cantidad indicada
            nombre, cantidad = cantidad, "1"
        equipos.append({"nombre": nombre.strip(), "cantidad": int(cantidad or 1)})
    return equipos


def listar_laboratorios(ruta_csv=CSV_LABORATORIOS):
    """Devuelve la lista de laboratorios con su capacidad y equipamiento."""
    with open(ruta_csv, newline="", encoding="utf-8-sig") as archivo:
        return [
            {
                "id": fila["id"].strip(),
                "nombre": fila["nombre"].strip(),
                "tipo": fila["tipo"].strip(),
                "edificio": fila["edificio"].strip(),
                "facultad": fila["facultad"].strip(),
                "capacidad": int(fila["capacidad"]),
                "equipos": _parsear_equipos(fila["equipos"]),
            }
            for fila in csv.DictReader(archivo)
        ]


def obtener_laboratorio(lab_id, ruta_csv=CSV_LABORATORIOS):
    """Devuelve un laboratorio por su id, o None si no existe."""
    return next((lab for lab in listar_laboratorios(ruta_csv) if lab["id"] == lab_id), None)

