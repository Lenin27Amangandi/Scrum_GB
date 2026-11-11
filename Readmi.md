## Sistema de reservas de laboratorios

Aplicación sencilla con Python y Flask en el backend, SQLite para guardar las
reservas, y HTML y CSS en el frontend.

El sistema impide reservar un laboratorio cuando existe otra reserva en la
misma fecha y las franjas horarias se cruzan. Al confirmar una reserva, la
franja queda guardada y aparece como bloqueada.

### Estructura

```text
Scrum_GB/
├── app.py
├── requirements.txt
├── reservas.db
├── templates/
│   └── index.html
└── static/
    └── style.css
```

### Ejecución

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Después, abre `http://127.0.0.1:5000` en el navegador.