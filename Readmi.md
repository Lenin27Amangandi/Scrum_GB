# FISLab-booking — integración HU-01, HU-03, HU-04, HU-05 y HU-06

Ejecutar `python3 -m pip install -r requirements.txt` y `python3 app.py`. Abrir http://127.0.0.1:5000.

El flujo principal integra catálogo CSV, formulario con correo @epn.edu.ec, código y motivo, reservas SQLite sin solapamiento, leyenda y franjas con colores, y comprobante con código persistente basado en el ID de reserva. La disponibilidad se consulta al cambiar fecha/laboratorio y cada 5 segundos. Los mantenimientos se leen de la tabla `mantenimientos` (laboratorio, fecha, hora_inicio, hora_fin); su administración no tiene interfaz. Se conservan los archivos originales del equipo y la demostración HU-03 en src/.

Pruebas: `npm test`, `python3 -m unittest discover -s backend/tests -v` y `python3 -m unittest discover -s tests -p 'test_*.py' -v`.

Verificar: seleccionar laboratorio y fecha, reservar con los campos completos, revisar comprobante, volver y seleccionar la misma fecha para ver rojo. Una reserva cruzada debe rechazarse. Sin reserva se muestra verde; un registro en mantenimientos se muestra amarillo y bloquea reservas.
