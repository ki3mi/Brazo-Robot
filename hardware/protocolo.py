import json

ENCODING = "utf-8"
END_OF_MESSAGE = "\n"


def build_kinematics_packet(mode, inputs, outputs):
    """Construye un mensaje JSON para enviar al ESP32."""
    packet = {
        "type": "kinematics",
        "mode": mode,
        "inputs": inputs,
        "outputs": outputs,
    }
    return (json.dumps(packet) + END_OF_MESSAGE).encode(ENCODING)


def parse_response(data):
    """Decodifica una respuesta JSON recibida del ESP32."""
    if not data:
        return None

    if isinstance(data, bytes):
        data = data.decode(ENCODING, errors="replace")

    try:
        return json.loads(data.strip())
    except json.JSONDecodeError:
        return {"raw": data.strip()}
