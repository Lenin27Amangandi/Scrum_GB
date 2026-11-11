import os
import tempfile
import unittest

_tmp = tempfile.TemporaryDirectory()
os.environ['RESERVAS_DATABASE'] = os.path.join(_tmp.name, 'test.db')
import app as sistema

class Integracion(unittest.TestCase):
    def test_flujo_completo(self):
        client = sistema.app.test_client()
        self.assertEqual(client.get('/').status_code, 200)
        labs = client.get('/api/laboratorios').get_json()
        lab = labs[0]['id']
        url = '/api/franjas?laboratorio=' + lab + '&fecha=2026-11-15'
        self.assertEqual(client.get(url).get_json()[1]['state'], 'disponible')
        data = dict(nombre='Estudiante', correo='estudiante@epn.edu.ec', codigo_unico='123', motivo='Practica', laboratorio=lab, fecha='2026-11-15', hora_inicio='09:00', hora_fin='10:00')
        response = client.post('/', data=data)
        self.assertIn(b'Comprobante de reserva', response.data)
        self.assertEqual(client.get(url).get_json()[1]['state'], 'ocupado')
        self.assertIn(b'ya est', client.post('/', data=data).data)
        with sistema.conectar() as db:
            db.execute('INSERT INTO mantenimientos (laboratorio, fecha, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)', (lab, '2026-11-15', '10:00', '11:00'))
        self.assertEqual(client.get(url).get_json()[2]['state'], 'mantenimiento')
        data.update(hora_inicio='10:00', hora_fin='11:00')
        self.assertNotIn(b'Comprobante de reserva', client.post('/', data=data).data)
        data.update(hora_inicio='11:00', hora_fin='12:00', correo='incorrecto@gmail.com')
        self.assertNotIn(b'Comprobante de reserva', client.post('/', data=data).data)
        self.assertEqual(client.get('/api/franjas?laboratorio=invalido&fecha=2026-11-15').status_code, 400)
