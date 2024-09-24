# utils.py
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def format_gps_data(gps_data):
    return f"Latitud: {gps_data['Latitud']:.6f}\n" \
           f"Longitud: {gps_data['Longitud']:.6f}\n" \
           f"Altitud: {gps_data['Altitud']} m\n" \
           f"Ángulo: {gps_data['Ángulo']}°\n" \
           f"Satélites: {gps_data['Satélites']}\n" \
           f"Velocidad: {gps_data['Velocidad']} km/h"

def format_io_data(io_data):
    return f"Código de Evento E/S: {io_data['Código de Evento E/S']}\n" \
           f"Número de Elementos E/S: {io_data['Número de Elementos E/S']}\n" \
           f"Elementos E/S: {io_data['Elementos E/S']}"