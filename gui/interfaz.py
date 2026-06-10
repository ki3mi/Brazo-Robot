import os
import sys
import tkinter as tk
from tkinter import ttk

# Este módulo construye únicamente la interfaz gráfica.
# Los cálculos de cinemática deben implementarse en otro archivo o módulo externo.
# Ejemplo de firma externa esperada:
#   external_inverse_kinematics(x, y, z) -> (q1, q2, q3, q4)
#   external_direct_kinematics(q1, q2, q3, q4) -> (x, y, z)
#
# El flujo de datos es:
# 1) el usuario ingresa valores en la interfaz,
# 2) un módulo de cinemática externo calcula las salidas,
# 3) la interfaz muestra esas salidas,
# 4) la interfaz envía los datos al ESP32 vía TCP/IP,
# 5) si el ESP32 devuelve datos, se muestran en el área de respuesta.


class RobotKinematicsGUI:
    def __init__(self, root):
        self.root = root
        root.title("Interfaz de Cinemática")
        root.resizable(False, False)

        self.style = ttk.Style(root)
        self.style.configure("TFrame", padding=12)
        self.style.configure("TButton", padding=6)
        self.style.configure("TLabel", padding=4)

        main_frame = ttk.Frame(root)
        main_frame.grid(row=0, column=0, sticky="NSEW")

        self._build_inverse_kinematics_section(main_frame)
        self._build_direct_kinematics_section(main_frame)
        self._build_esp32_response_section(main_frame)

        # Callbacks que main.py puede instalar:
        # - self.on_inverse(x, y, z) -> (q1, q2, q3, q4) or (None, ..)
        # - self.on_direct(q1,q2,q3,q4) -> (x,y,z) or (None,..)
        # - self.on_send(mode, inputs, outputs) -> response (dict) or None
        self.on_inverse = None
        self.on_direct = None
        self.on_send = None

    def _build_esp32_response_section(self, parent):
        response_frame = ttk.Frame(parent)
        response_frame.grid(row=2, column=0, padx=8, pady=(0, 8), sticky="EW")

        response_label = ttk.Label(response_frame, text="Respuesta ESP32:")
        response_label.grid(row=0, column=0, sticky="W")

        self.esp_response_value = ttk.Label(response_frame, text="---", width=60, relief="sunken")
        self.esp_response_value.grid(row=0, column=1, sticky="W", padx=(8, 0))

    def _build_inverse_kinematics_section(self, parent):
        inverse_frame = ttk.Labelframe(parent, text="Cinemática Inversa")
        inverse_frame.grid(row=0, column=0, padx=8, pady=8, sticky="NSEW")

        self.inv_inputs = {}
        for index, label_text in enumerate(("x", "y", "z")):
            label = ttk.Label(inverse_frame, text=label_text)
            label.grid(row=index, column=0, sticky="W")
            entry = ttk.Entry(inverse_frame, width=16)
            entry.grid(row=index, column=1, sticky="W")
            self.inv_inputs[label_text] = entry

        calc_button = ttk.Button(
            inverse_frame,
            text="Calcular Inversa",
            command=self._calculate_inverse_kinematics,
        )
        calc_button.grid(row=3, column=0, columnspan=2, pady=(8, 12), sticky="EW")

        self.inv_outputs = {}
        for index, joint in enumerate(("q1", "q2", "q3", "q4")):
            label = ttk.Label(inverse_frame, text=joint)
            label.grid(row=index, column=2, sticky="W", padx=(16, 4))
            # Campo de salida donde se mostrará el valor calculado para esta articulación
            value = ttk.Label(inverse_frame, text="---", width=18, relief="sunken")
            value.grid(row=index, column=3, sticky="W")
            self.inv_outputs[joint] = value

    def _build_direct_kinematics_section(self, parent):
        direct_frame = ttk.Labelframe(parent, text="Cinemática Directa")
        direct_frame.grid(row=1, column=0, padx=8, pady=8, sticky="NSEW")

        self.dir_inputs = {}
        for index, label_text in enumerate(("q1", "q2", "q3", "q4")):
            label = ttk.Label(direct_frame, text=label_text)
            label.grid(row=index, column=0, sticky="W")
            entry = ttk.Entry(direct_frame, width=16)
            entry.grid(row=index, column=1, sticky="W")
            self.dir_inputs[label_text] = entry

        calc_button = ttk.Button(
            direct_frame,
            text="Calcular Directa",
            command=self._calculate_direct_kinematics,
        )
        calc_button.grid(row=4, column=0, columnspan=2, pady=(8, 12), sticky="EW")

        self.dir_outputs = {}
        for index, label_text in enumerate(("x", "y", "z")):
            label = ttk.Label(direct_frame, text=label_text)
            label.grid(row=index, column=2, sticky="W", padx=(16, 4))
            # Campo de salida donde se mostrará el valor calculado para esta coordenada
            value = ttk.Label(direct_frame, text="---", width=18, relief="sunken")
            value.grid(row=index, column=3, sticky="W")
            self.dir_outputs[label_text] = value

    def _parse_float(self, entry):
        try:
            return float(entry.get().strip())
        except ValueError:
            return None

    def _calculate_inverse_kinematics(self):
        x = self._parse_float(self.inv_inputs["x"])
        y = self._parse_float(self.inv_inputs["y"])
        z = self._parse_float(self.inv_inputs["z"])

        if x is None or y is None or z is None:
            self._set_inverse_outputs(None, None, None, None)
            self._set_esp_status("Valores de entrada inválidos para cinemática inversa.")
            return

        # Llamada a callback instalado desde main.py
        if callable(self.on_inverse):
            q1, q2, q3, q4 = self.on_inverse(x, y, z)
        else:
            q1, q2, q3, q4 = (None, None, None, None)

        # Mostrar resultados en la interfaz
        self._set_inverse_outputs(q1, q2, q3, q4)

        # Enviar al microcontrolador si hay callback de envío registrado
        if None not in (q1, q2, q3, q4) and callable(self.on_send):
            response = self.on_send(
                "inverse",
                {"x": x, "y": y, "z": z},
                {"q1": q1, "q2": q2, "q3": q3, "q4": q4},
            )
            if response is None:
                self._set_esp_status("No se recibió respuesta del ESP32.")
            else:
                self._set_esp_response(response)
        elif None in (q1, q2, q3, q4):
            self._set_esp_status("Cálculos de cinemática inversa no implementados.")

    def _calculate_direct_kinematics(self):
        q1 = self._parse_float(self.dir_inputs["q1"])
        q2 = self._parse_float(self.dir_inputs["q2"])
        q3 = self._parse_float(self.dir_inputs["q3"])
        q4 = self._parse_float(self.dir_inputs["q4"])

        if q1 is None or q2 is None or q3 is None or q4 is None:
            self._set_direct_outputs(None, None, None)
            self._set_esp_status("Valores de entrada inválidos para cinemática directa.")
            return

        # Llamada a callback instalado desde main.py
        if callable(self.on_direct):
            x, y, z = self.on_direct(q1, q2, q3, q4)
        else:
            x, y, z = (None, None, None)

        # Mostrar resultados en la interfaz
        self._set_direct_outputs(x, y, z)

        # Enviar al microcontrolador si existe callback de envío
        if None not in (x, y, z) and callable(self.on_send):
            response = self.on_send(
                "direct",
                {"q1": q1, "q2": q2, "q3": q3, "q4": q4},
                {"x": x, "y": y, "z": z},
            )
            if response is None:
                self._set_esp_status("No se recibió respuesta del ESP32.")
            else:
                self._set_esp_response(response)
        elif None in (x, y, z):
            self._set_esp_status("Cálculos de cinemática directa no implementados.")

    def _external_inverse_kinematics(self, x, y, z):
        # ================================================================================
        # Reemplaza este stub con la llamada al módulo externo de cálculos.
        # Debe devolver una tupla (q1, q2, q3, q4).
        # ================================================================================
        return None, None, None, None

    def _external_direct_kinematics(self, q1, q2, q3, q4):
        # =================================================================================
        # Reemplaza este stub con la llamada al módulo externo de cálculos.
        # Debe devolver una tupla (x, y, z).
        # =================================================================================
        return None, None, None

    def _send_kinematics_to_esp32(self, mode, inputs, outputs):
        # Envía el paquete de entrada/salida al ESP32 y muestra la respuesta recibida.
        try:
            response = self.esp_client.send_kinematics(mode, inputs, outputs)
            if response is None:
                self._set_esp_status("No se recibió respuesta del ESP32.")
            else:
                self._set_esp_response(response)
        except Exception as error:
            self._set_esp_status(f"Error de conexión ESP32: {error}")

    def _set_esp_response(self, response):
        # Muestra la respuesta del ESP32 en la interfaz.
        if isinstance(response, dict):
            text = str(response)
        else:
            text = f"{response}"
        self.esp_response_value.config(text=text)

    def _set_esp_status(self, message):
        # Muestra un mensaje de estado cuando no hay respuesta útil del ESP32.
        self.esp_response_value.config(text=message)

    def _set_inverse_outputs(self, q1, q2, q3, q4):
        # Aquí se muestran los valores de salida de la cinemática inversa
        values = (q1, q2, q3, q4)
        for joint, value in zip(("q1", "q2", "q3", "q4"), values):
            text = f"{value:.3f}" if value is not None else "No implementado"
            self.inv_outputs[joint].config(text=text)

    def _set_direct_outputs(self, x, y, z):
        # Aquí se muestran los valores de salida de la cinemática directa
        values = (x, y, z)
        for label, value in zip(("x", "y", "z"), values):
            text = f"{value:.3f}" if value is not None else "No implementado"
            self.dir_outputs[label].config(text=text)


if __name__ == "__main__":
    root = tk.Tk()
    RobotKinematicsGUI(root)
    root.mainloop()