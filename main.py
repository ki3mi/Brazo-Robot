import argparse
import traceback
import tkinter as tk

from gui.interfaz import RobotKinematicsGUI
from hardware.serial_controller import Esp32TcpClient

# Por el momento NO usar `robot.cinematica` — forzamos stubs deshabilitados.
# Cuando quieras activar el módulo de cinemática, quita esta sección y descomenta
# la importación en el bloque siguiente.
cinematica_module = None
has_cinematica = False

# Si en el futuro quieres habilitar `robot.cinematica`, reemplaza lo anterior
# por la importación condicional:
# try:
#     from robot import cinematica as cinematica_module
#     has_cinematica = True
# except Exception:
#     cinematica_module = None
#     has_cinematica = False


def make_inverse_callback():
    if not has_cinematica:
        return lambda x, y, z: (None, None, None, None)

    def cb(x, y, z):
        try:
            return cinematica_module.inverse_kinematics(x, y, z)
        except Exception:
            traceback.print_exc()
            return (None, None, None, None)

    return cb


def make_direct_callback():
    if not has_cinematica:
        return lambda q1, q2, q3, q4: (None, None, None)

    def cb(q1, q2, q3, q4):
        try:
            return cinematica_module.direct_kinematics(q1, q2, q3, q4)
        except Exception:
            traceback.print_exc()
            return (None, None, None)

    return cb


def make_send_callback(esp_client: Esp32TcpClient):
    def send_cb(mode, inputs, outputs):
        try:
            return esp_client.send_kinematics(mode, inputs, outputs)
        except Exception as e:
            print(f"Error enviando datos al ESP32: {e}")
            return None

    return send_cb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="192.168.4.1", help="IP del ESP32")
    parser.add_argument("--port", default=12345, type=int, help="Puerto TCP del ESP32")
    args = parser.parse_args()

    esp_client = Esp32TcpClient(host=args.host, port=args.port)

    root = tk.Tk()
    gui = RobotKinematicsGUI(root)

    # Conectar callbacks
    gui.on_inverse = make_inverse_callback()
    gui.on_direct = make_direct_callback()
    gui.on_send = make_send_callback(esp_client)

    root.mainloop()


if __name__ == "__main__":
    main()
