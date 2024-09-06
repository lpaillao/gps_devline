import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def format_gps_data(gps_data):
    return f"  Latitude: {gps_data['Latitude']:.6f}\n" \
           f"  Longitude: {gps_data['Longitude']:.6f}\n" \
           f"  Altitude: {gps_data['Altitude']} m\n" \
           f"  Angle: {gps_data['Angle']}°\n" \
           f"  Satellites: {gps_data['Satellites']}\n" \
           f"  Speed: {gps_data['Speed']} km/h"

def format_io_data(io_data):
    formatted = f"  I/O Event Code: {io_data['I/O Event Code']}\n" \
                f"  Number of I/O Elements: {io_data['Number of I/O Elements']}\n" \
                "  I/O Elements:"
    
    for code, value in io_data['I/O Elements'].items():
        formatted += f"\n    Code {code}: {value}"
    
    return formatted