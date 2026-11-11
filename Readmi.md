# Scrum GB — HU-03: Indicador visual de estado

Implementación inicial en HTML, CSS y JavaScript sin dependencias. El repositorio de partida solo contenía este archivo vacío y no tenía aplicación ni arquitectura previa.

## Ejecutar

Con Python 3 y Node.js 18 o superior disponibles:

```sh
npm start
```

Abrir http://localhost:8000. Para ejecutar las pruebas: `npm test`.

## Verificación manual

1. Comprobar que la leyenda está visible: verde Disponible, rojo Ocupado y amarillo Mantenimiento.
2. Comprobar los tres estados en las franjas iniciales, con color y texto para no depender exclusivamente del color.
3. Cambiar cada selector entre los tres estados: el borde y la etiqueta deben actualizarse inmediatamente, sin recargar ni cambiar otras franjas.
4. Recorrer los selectores con Tab y cambiar estados con el teclado; los cambios se anuncian a lectores de pantalla.
5. Reducir la ventana a tamaño móvil y comprobar que la leyenda y las franjas siguen siendo legibles.

## Estructura e integración

- `src/schedule.js`: modelo de horarios, validación y suscripciones a cambios.
- `src/app.js`: presentación y actualización del indicador cuando cambia el modelo.
- `src/styles.css`: colores compartidos por indicadores y leyenda, diseño adaptable y foco visible.
- `tests/schedule.test.js`: estados iniciales, todas las transiciones, aislamiento, validación y suscripciones.

Los horarios son datos de demostración en memoria: al recargar se restablecen. No existe backend, autenticación ni sincronización entre usuarios. Una futura fuente de datos puede aplicar los estados mediante `schedule.setState(id, estado)` en la capa de aplicación; los suscriptores actualizan la vista.
