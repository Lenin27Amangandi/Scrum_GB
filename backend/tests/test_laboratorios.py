"""Pruebas de la HU-01: Catálogo de Laboratorios.

Ejecutar:  python -m unittest discover -s backend/tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from repositorio import _parsear_equipos, listar_laboratorios, obtener_laboratorio  # noqa: E402


class TestCatalogoLaboratorios(unittest.TestCase):
    def setUp(self):
        self.labs = listar_laboratorios()

    def test_incluye_los_cuatro_tipos(self):
        tipos = {lab["tipo"] for lab in self.labs}
        self.assertTrue({"Redes", "Software", "Electronica", "Fisica"} <= tipos)

    def test_cada_lab_cumple_criterios_de_aceptacion(self):
        for lab in self.labs:
            with self.subTest(lab=lab["id"]):
                self.assertTrue(lab["nombre"])
                self.assertTrue(lab["edificio"])
                self.assertTrue(lab["facultad"])
                self.assertGreater(lab["capacidad"], 0)
                self.assertGreater(len(lab["equipos"]), 0)

    def test_parseo_de_equipos(self):
        self.assertEqual(
            _parsear_equipos("Osciloscopio:10; Multímetro:20"),
            [{"nombre": "Osciloscopio", "cantidad": 10}, {"nombre": "Multímetro", "cantidad": 20}],
        )
        self.assertEqual(_parsear_equipos(""), [])

    def test_obtener_laboratorio(self):
        self.assertEqual(obtener_laboratorio("LAB-RED-01")["tipo"], "Redes")
        self.assertIsNone(obtener_laboratorio("NO-EXISTE"))


if __name__ == "__main__":
    unittest.main()

