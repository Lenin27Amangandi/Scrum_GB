# FISLab-booking - Sistema de Reserva de Laboratorios EPN

## Ejecutar
```bash
python backend/app.py
```
Abrir http://localhost:8000

## Pruebas
```bash
python -m unittest discover -s backend/tests -v
```

## Estructura
```
backend/
  app.py              Servidor HTTP (API + frontend), solo librería estándar
  repositorio.py      Lectura del CSV
  data/laboratorios.csv
  tests/
frontend/
  index.html  styles.css  app.js
```

## API
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/laboratorios` | Lista de laboratorios (HU-01) |
| GET | `/api/laboratorios/<id>` | Detalle de un laboratorio |

## Formato del CSV
`equipos` usa `Nombre:cantidad` separados por `;`, por ejemplo `Osciloscopio:10;Multímetro:20`.

