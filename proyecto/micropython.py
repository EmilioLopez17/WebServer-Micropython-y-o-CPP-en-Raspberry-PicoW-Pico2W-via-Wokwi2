import network
import socket
import time
import os

# --- CONFIGURACIÓN ---
SSID = 'TecNM-ITT'
PASSWORD = ''
ARCHIVO_DATOS = 'datos.txt'


def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Conectando a WiFi...", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)

    ip = wlan.ifconfig()[0]
    print("\nConectado!")
    print(f"Dirección IP del Pico: {ip}")
    return ip


def leer_archivo(nombre):
    try:
        with open(nombre, 'r') as f:
            return f.read()
    except OSError:
        return "ERROR: Archivo no encontrado."


def iniciar_servidor(ip):
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    # Permitir reutilizar el socket inmediatamente tras cerrar
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    print(f"Servidor HTTP escuchando en http://{ip}:80/archivo")

    while True:
        try:
            cl, addr_client = s.accept()
            request = cl.recv(1024).decode('utf-8')

            # Simple router
            if 'GET /archivo' in request:
                contenido = leer_archivo(ARCHIVO_DATOS)
                # Respuesta con CORS habilitado para que la web pueda leer los datos
                response = "HTTP/1.1 200 OK\r\n"
                response += "Content-Type: text/plain\r\n"
                response += "Access-Control-Allow-Origin: *\r\n"
                response += f"Content-Length: {len(contenido)}\r\n"
                response += "\r\n"
                response += contenido
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"

            cl.send(response)
            cl.close()
        except Exception as e:
            print(f"Error en servidor: {e}")
            if 'cl' in locals():
                cl.close()


# Ejecución principal
try:
    ip_pico = conectar_wifi()
    iniciar_servidor(ip_pico)
except KeyboardInterrupt:
    print("\nServidor detenido.")

