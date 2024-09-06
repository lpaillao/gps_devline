class Decoder:
    @staticmethod
    def decode(data):
        # Implementación básica de decodificación
        # Ajusta esto según el formato específico de tus dispositivos GPS
        try:
            decoded = data.decode().strip().split(',')
            if len(decoded) < 6:
                return None
            return {
                "latitude": float(decoded[0]),
                "longitude": float(decoded[1]),
                "speed": float(decoded[2]),
                "direction": float(decoded[3]),
                "altitude": float(decoded[4]),
                "satellite_count": int(decoded[5])
            }
        except Exception as e:
            print(f"Error decoding GPS data: {e}")
            return None