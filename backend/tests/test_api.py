"""Pruebas del endpoint /api/laboratorios sin abrir sockets (HU-01)."""

import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app  # noqa: E402


class _ManejadorFalso(app.Manejador):
    """Ejecuta el manejador con buffers en memoria en lugar de un socket real."""

    def __init__(self, ruta):
        self.rfile = io.BytesIO(f"GET {ruta} HTTP/1.1\r\nHost: test\r\n\r\n".encode())
        self.wfile = io.BytesIO()
        self.client_address = ("127.0.0.1", 0)
        self.directory = str(app.FRONTEND_DIR)
        self.server = None
        self.handle_one_request()

    def log_message(self, *args):  # Silenciar logs en pruebas
        pass

    def respuesta(self):
        cabecera, _, cuerpo = self.wfile.getvalue().partition(b"\r\n\r\n")
        codigo = int(cabecera.split(b" ")[1])
        return codigo, cabecera.decode("latin-1"), cuerpo


class TestApiLaboratorios(unittest.TestCase):
    def test_lista_laboratorios(self):
        codigo, cabecera, cuerpo = _ManejadorFalso("/api/laboratorios").respuesta()
        self.assertEqual(codigo, 200)
        self.assertIn("application/json", cabecera)
        datos = json.loads(cuerpo)
        self.assertGreaterEqual(len(datos), 4)
        self.assertTrue({"nombre", "edificio", "facultad", "capacidad", "equipos"} <= datos[0].keys())

    def test_detalle_y_404(self):
        self.assertEqual(_ManejadorFalso("/api/laboratorios/LAB-SW-01").respuesta()[0], 200)
        self.assertEqual(_ManejadorFalso("/api/laboratorios/NO-EXISTE").respuesta()[0], 404)

    def test_sirve_frontend(self):
        codigo, _, cuerpo = _ManejadorFalso("/").respuesta()
        self.assertEqual(codigo, 200)
        self.assertIn(b"Cat\xc3\xa1logo de Laboratorios", cuerpo)


if __name__ == "__main__":
    unittest.main()

