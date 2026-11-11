"""Servidor FISLab-booking: API REST + archivos estáticos del frontend.

Ejecutar:  python backend/app.py   ->   http://localhost:8000
"""

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from repositorio import listar_laboratorios, obtener_laboratorio

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
HOST, PUERTO = "localhost", 8000


class Manejador(SimpleHTTPRequestHandler):
    def do_GET(self):
        ruta = urlparse(self.path).path.rstrip("/")

        # GET /api/laboratorios  -> lista completa (HU-01)
        if ruta == "/api/laboratorios":
            return self._responder_json(200, listar_laboratorios())

        # GET /api/laboratorios/<id>  -> detalle de un laboratorio
        if ruta.startswith("/api/laboratorios/"):
            lab = obtener_laboratorio(ruta.split("/")[-1])
            if lab is None:
                return self._responder_json(404, {"error": "Laboratorio no encontrado"})
            return self._responder_json(200, lab)

        if ruta.startswith("/api/"):
            return self._responder_json(404, {"error": "Ruta no encontrada"})

        # Cualquier otra ruta: archivos del frontend (index.html, css, js)
        return super().do_GET()

    def _responder_json(self, codigo, datos):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)


def main():
    servidor = ThreadingHTTPServer((HOST, PUERTO), partial(Manejador, directory=str(FRONTEND_DIR)))
    print(f"FISLab-booking corriendo en http://{HOST}:{PUERTO}  (Ctrl+C para detener)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()

