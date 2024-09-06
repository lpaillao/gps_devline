# GPS Server

Este es un servidor GPS para gestionar y controlar dispositivos GPS.

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual: `python3 -m venv venv`
3. Activar el entorno virtual: `source venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`

## Ejecución

Para ejecutar el servidor:

```
python src/main.py
```

wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo tee /etc/apt/trusted.gpg.d/mongodb-server-6.0.asc
sudo apt update
sudo apt install -y mongodb-org


sudo apt install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb