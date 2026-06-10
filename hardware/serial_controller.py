import socket
from typing import Any, Dict, Optional

from .protocolo import build_kinematics_packet, parse_response


class Esp32TcpClient:
    def __init__(self, host: str = "192.168.4.1", port: int = 12345, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def send_kinematics(self, mode: str, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Envía los datos de cinemática y devuelve la respuesta del ESP32 si existe."""
        payload = build_kinematics_packet(mode, inputs, outputs)
        return self._send_payload(payload)

    def _send_payload(self, payload: bytes) -> Optional[Dict[str, Any]]:
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
            sock.sendall(payload)
            return self._receive_response(sock)

    def _receive_response(self, sock: socket.socket) -> Optional[Dict[str, Any]]:
        buffer = b""
        sock.settimeout(self.timeout)

        while True:
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                break

            if not chunk:
                break

            buffer += chunk
            if b"\n" in buffer:
                break

        if not buffer:
            return None

        # Tomamos solo hasta el primer delimitador de fin de mensaje
        line, _, _ = buffer.partition(b"\n")
        return parse_response(line)
