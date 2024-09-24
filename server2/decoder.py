# Decoder.py
from datetime import datetime
import logging

class Decoder:
    def __init__(self, carga_util, imei):
        self.carga_util = carga_util
        self.imei = imei
        self.precision = 10000000.0

    def decodificar_datos(self):
        logging.debug(f"Carga útil sin procesar: {self.carga_util}")

        if len(self.carga_util) < 20:
            logging.warning("Carga útil demasiado corta para contener datos válidos")
            return []

        numero_de_registros = int(self.carga_util[18:20], 16)
        numero_de_registros_final = int(self.carga_util[-10:-8], 16) if len(self.carga_util) >= 10 else 0
        logging.info(f"Número de registros: {numero_de_registros}, Número final: {numero_de_registros_final}")

        datos_avl = self.carga_util[20:-10]
        logging.debug(f"Datos AVL: {datos_avl}")

        registros = []
        if numero_de_registros == numero_de_registros_final:
            posicion = 0
            for _ in range(numero_de_registros):
                if posicion >= len(datos_avl):
                    logging.warning(f"Fin inesperado de datos en la posición {posicion}")
                    break
                try:
                    registro = self._decodificar_registro_individual(datos_avl[posicion:])
                    registros.append(registro)
                    longitud_registro = self._obtener_longitud_registro(datos_avl[posicion:])
                    if longitud_registro is None:
                        logging.warning(f"No se puede determinar la longitud del registro en la posición {posicion}")
                        break
                    posicion += longitud_registro
                    logging.info(f"Registro decodificado: {registro}")
                except Exception as e:
                    logging.error(f"Error al decodificar el registro: {e}")
                    break
        else:
            logging.warning(f"Discrepancia en el número de registros: inicio={numero_de_registros}, fin={numero_de_registros_final}")

        return registros

    def _decodificar_registro_individual(self, datos_registro):
        if len(datos_registro) < 46:
            raise ValueError("Datos insuficientes para decodificar un registro individual")

        marca_tiempo = self._decodificar_marca_tiempo(datos_registro[0:16])
        prioridad = int(datos_registro[16:18], 16)
        datos_gps = self._decodificar_datos_gps(datos_registro[18:46])
        datos_io = self._decodificar_datos_io(datos_registro[46:])

        return {
            "IMEI": self.imei,
            "FechaHora": marca_tiempo.isoformat(),
            "Prioridad": prioridad,
            "Datos GPS": datos_gps,
            "Datos E/S": datos_io
        }
    def _decodificar_marca_tiempo(self, marca_tiempo_hex):
        marca_tiempo_int = int(marca_tiempo_hex, 16)
        return datetime.utcfromtimestamp(marca_tiempo_int/1000)

    def _decodificar_datos_gps(self, datos_gps):
        return {
            "Longitud": int(datos_gps[0:8], 16) / self.precision,
            "Latitud": int(datos_gps[8:16], 16) / self.precision,
            "Altitud": int(datos_gps[16:20], 16),
            "Ángulo": int(datos_gps[20:24], 16),
            "Satélites": int(datos_gps[24:26], 16),
            "Velocidad": int(datos_gps[26:28], 16)
        }

    def _decodificar_datos_io(self, datos_io):
        if len(datos_io) < 4:
            return {"Código de Evento E/S": 0, "Número de Elementos E/S": 0, "Elementos E/S": {}}

        posicion = 0
        codigo_evento_io = int(datos_io[posicion:posicion+2], 16)
        posicion += 2

        numero_elementos_io = int(datos_io[posicion:posicion+2], 16)
        posicion += 2

        elementos_io = {}
        for tamano_bit in [1, 2, 4, 8]:
            if posicion + 2 > len(datos_io):
                break
            num_elementos = int(datos_io[posicion:posicion+2], 16)
            posicion += 2
            for _ in range(num_elementos):
                if posicion + 2 + 2*tamano_bit > len(datos_io):
                    break
                codigo_io = int(datos_io[posicion:posicion+2], 16)
                posicion += 2
                valor_io = int(datos_io[posicion:posicion+2*tamano_bit], 16)
                posicion += 2 * tamano_bit
                elementos_io[codigo_io] = valor_io

        return {
            "Código de Evento E/S": codigo_evento_io,
            "Número de Elementos E/S": numero_elementos_io,
            "Elementos E/S": elementos_io
        }

    def _obtener_longitud_registro(self, datos_registro):
        if len(datos_registro) < 23:
            logging.warning("Datos de registro demasiado cortos")
            return None

        # Un registro individual consta de:
        # 8 bytes (marca de tiempo) + 1 byte (prioridad) + 14 bytes (datos GPS) + datos E/S variables
        inicio_datos_io = 23
        if len(datos_registro) < inicio_datos_io + 4:
            logging.warning("Datos insuficientes para los datos E/S")
            return None

        try:
            elementos_evento_io = int(datos_registro[inicio_datos_io+2:inicio_datos_io+4], 16)
            longitud_datos_io = 4  # Código de evento E/S (1 byte) + Número de elementos E/S (1 byte)
            
            posicion = inicio_datos_io + 4
            for tamano_bit in [1, 2, 4, 8]:
                if posicion + 2 > len(datos_registro):
                    logging.warning(f"Fin inesperado de datos en la posición {posicion}")
                    return None
                num_elementos = int(datos_registro[posicion:posicion+2], 16)
                posicion += 2
                longitud_elemento = 1 + tamano_bit  # 1 byte para el ID del elemento + tamaño del valor
                longitud_datos_io += 2 + num_elementos * longitud_elemento
                if posicion + num_elementos * longitud_elemento > len(datos_registro):
                    logging.warning(f"Datos insuficientes para elementos de {tamano_bit} bytes")
                    return None
                posicion += num_elementos * longitud_elemento

            longitud_total = inicio_datos_io + longitud_datos_io
            if longitud_total <= len(datos_registro):
                return longitud_total
            else:
                logging.warning(f"Longitud calculada ({longitud_total}) excede la longitud de los datos ({len(datos_registro)})")
                return None

        except ValueError as e:
            logging.error(f"Error al convertir datos a entero: {e}")
            return None
        except Exception as e:
            logging.error(f"Error inesperado al obtener longitud del registro: {e}")
            return None