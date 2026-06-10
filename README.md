Proyecto: Brazo_robot
=====================

Resumen
------
Interfaz gráfica en Tkinter para calcular y enviar datos de cinemática de un manipulador a un ESP32 vía TCP/IP. La lógica de cinemática está separada y por ahora está deshabilitada; `main.py` centraliza la ejecución y conecta la GUI con el controlador de red.

Estructura del repositorio
-------------------------
- main.py — Punto de entrada. Conecta GUI, controlador ESP y (opcional) módulo de cinemática.
- requirements.txt — Dependencias Python (SymPy, IPython, NumPy, Matplotlib).
- Instructions.txt — Archivo de instrucciones adicionales (se mantiene tal cual).
- gui/
  - interfaz.py — Interfaz Tkinter (entradas, salidas, y áreas de respuesta). No debe realizar cálculos, expone callbacks.
  - test.py — utilidades de prueba (si procede).
- hardware/
  - protocolo.py — Formato de mensaje JSON y utilidades de serialización/parsing.
  - serial_controller.py — Cliente TCP `Esp32TcpClient` que envía/recibe paquetes al ESP32.
- robot/
  - cinematica.py — (opcional/no activo) módulo donde se implementarán `inverse_kinematics` y `direct_kinematics`.

Requisitos
----------
- Python 3.13 (el proyecto fue probado con 3.13 en Windows).
- Tcl/Tk instalado (para `tkinter`). En Windows suele instalarse con Python estándar.

Instalación rápida (Windows)
---------------------------
Desde la carpeta raíz del proyecto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate
python -m pip install -r requirements.txt
```

Ejecución
---------
Por defecto el `main.py` intenta conectar al ESP32 en `192.168.4.1:12345`. Puedes especificar host y puerto:

```powershell
python main.py --host 192.168.4.1 --port 12345
# o
python main.py
```

Flujo de datos (arquitectura)
----------------------------
La aplicación sigue una arquitectura modular y orientada a responsabilidades:

- main.py (coordinador)
  - Crea instancia de la GUI (`gui/interfaz.py`) y del controlador de red (`hardware/serial_controller.py`).
  - Registra tres callbacks sobre la GUI:
    - `on_inverse(x,y,z)` — devuelve `(q1,q2,q3,q4)`; implementado por el módulo de cinemática si está disponible.
    - `on_direct(q1,q2,q3,q4)` — devuelve `(x,y,z)`; implementado por el módulo de cinemática si está disponible.
    - `on_send(mode, inputs, outputs)` — envía los datos al ESP32 y devuelve la respuesta.

- GUI (`gui/interfaz.py`)
  - Exclusivamente responsable de mostrar campos de entrada/salida y de invocar callbacks.
  - No realiza cálculos ni comunicaciones por sí misma — solo muestra el resultado devuelto por callbacks y muestra respuestas del ESP32.

- Módulo de cinemática (`robot/cinematica.py`) — (opcional)
  - Debe implementar dos funciones públicas:
    - `inverse_kinematics(x, y, z) -> (q1, q2, q3, q4)`
    - `direct_kinematics(q1, q2, q3, q4) -> (x, y, z)`
  - main.py intenta importarlo solo si lo habilitas. Por ahora la importación está desactivada.

- Controlador de red (`hardware/serial_controller.py`) y protocolo (`hardware/protocolo.py`)
  - `Esp32TcpClient.send_kinematics(mode, inputs, outputs)` empaqueta en JSON y envía por TCP; espera una respuesta terminada en `\n` y la parsea.

Notas y solución de problemas
----------------------------
- Error común con `tkinter`: "Can't find a usable init.tcl" — normalmente indica que Tcl/Tk no está instalado en la misma distribución de Python usada. Verifica que ejecutas la app con el Python correcto (el que tiene Tcl/Tk) o reinstala Python incluyendo Tcl/Tk.

- Si la GUI se bloquea al enviar datos (espera sincrónica por la respuesta), considera ejecutar el envío en un hilo aparte o usar IO asíncrono. Actualmente `Esp32TcpClient` realiza conexiones sincrónicas.

- Para simular el ESP32 durante pruebas, puedes usar `nc -l -p 12345` (netcat) o un script Python simple que acepte conexiones y responda con un JSON terminado en `\n`.

Cómo reactivar `robot/cinematica.py`
-----------------------------------
1. Implementa las funciones `inverse_kinematics` y `direct_kinematics` en `robot/cinematica.py`.
2. En `main.py`, quita el comentario de la sección con la importación condicional (la guía está comentada dentro del archivo).

Archivos modificados/creados por esta entrega
-------------------------------------------
- [README.md](README.md) (este archivo)
- [main.py](main.py) (coordinador)
- [gui/interfaz.py](gui/interfaz.py) (refactorizado para callbacks)
- [hardware/protocolo.py](hardware/protocolo.py)
- [hardware/serial_controller.py](hardware/serial_controller.py)
- [requirements.txt](requirements.txt) (ya presente)
- [Instructions.txt](Instructions.txt) (sin cambios)

Contacto rápido
---------------
Si quieres, puedo:
- Añadir stubs de prueba para `robot/cinematica.py` que devuelvan valores fijos.
- Hacer el envío al ESP32 en un hilo para evitar bloquear la GUI.
- Añadir un `README` en español más corto o un `USAGE.md` separado.

