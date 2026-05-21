## 1) Resumen ejecutivo

Se implementó una arquitectura cliente-servidor ligera para lectura remota de información operativa almacenada en `datos.txt`. El sistema se compone de:

1. **Servidor embebido en MicroPython** (Pico W), que expone un endpoint HTTP `GET /archivo`.
2. **Interfaz web (dashboard)** en HTML/CSS/JavaScript, que consulta periódicamente el endpoint y renderiza el contenido línea por línea.
3. **Archivo fuente de datos (`datos.txt`)**, que representa el estado del sistema monitoreado.

La solución es apta para simulación en Wokwi y para despliegue real en red local WiFi.

---

## 2) Objetivo general

Diseñar e implementar un WebServer en MicroPython para Raspberry Pi Pico W que entregue datos de monitoreo en tiempo real (o casi real) hacia una interfaz web moderna, con mecanismos de actualización manual y automática.

---

## 3) Arquitectura de la solución

### 3.1 Vista general

- **Capa de adquisición / fuente:** `datos.txt` (estado y logs del sistema).
- **Capa de servicio:** script MicroPython (conexión WiFi + socket HTTP + lectura de archivo).
- **Capa de presentación:** dashboard web responsivo (Tailwind + JS nativo).

### 3.2 Flujo de datos

1. El Pico W se conecta a la red WiFi.
2. Inicia servidor en puerto 80.
3. Cliente web solicita `http://<ip-del-pico>/archivo`.
4. El servidor lee `datos.txt` y responde `text/plain` con CORS habilitado.
5. El frontend divide el texto en líneas y lo dibuja en un visor tipo terminal.
6. El usuario puede refrescar manualmente o activar auto-refresh.

---

## 4) Documentación formal por archivo

## 4.1 Archivo de interfaz web (HTML + CSS + JS)

### 4.1.1 Propósito
Proveer una UIX de monitoreo con estilo de consola/operación técnica, capaz de conectarse dinámicamente a la IP del Pico W y mostrar el contenido del archivo remoto.

### 4.1.2 Componentes funcionales

- **Barra superior (AppBar):** identidad del sistema (`PICO_OS v1.0`) y estado visual de conexión.
- **Sidebar:** navegación ficticia de módulos (telemetría, filesystem, red, logs).
- **Barra de conexión:**
  - Campo editable de IP del nodo.
  - Botón `Update Endpoint` para reconfigurar la URL.
  - Botón `Fetch Data` para consulta bajo demanda.
  - Botón `Clear View` para limpieza del visor.
- **Visor de archivo:**
  - Muestra ruta lógica (`/mnt/sd/datos.txt`).
  - Renderizado de contenido con número de línea.
  - Toggle de auto-refresh.
- **Status bar:** último sync, tamaño de datos y metadatos simulados.

### 4.1.3 Funciones JavaScript

- `updateEndpoint()`:
  - Lee la IP capturada.
  - Construye `endpoint = http://<ip>/archivo`.
  - Actualiza la IP mostrada en sidebar.
  - Ejecuta `fetchData()` inmediatamente.

- `fetchData()`:
  - Realiza `fetch(endpoint)`.
  - Valida `response.ok`.
  - Convierte respuesta a texto y la separa por líneas.
  - Inserta en el DOM cada línea con numeración.
  - Actualiza hora de sincronización y tamaño de carga.
  - Maneja errores de conectividad y presenta mensaje guía.

- `clearView()`:
  - Limpia la vista de contenido.

- `escapeHtml(text)`:
  - Evita inyección HTML al renderizar texto remoto.

- Evento `auto-refresh`:
  - Activa `setInterval(fetchData, 2000)` al habilitar.
  - Cancela intervalo al deshabilitar.

### 4.1.4 Criterios técnicos relevantes

- Separación clara entre capa visual y lógica de consulta.
- Protección básica XSS mediante escape de texto.
- Operación sin frameworks JS pesados (baja complejidad para entorno académico).
- Diseño coherente para demostrar una interfaz de monitoreo de contexto industrial.

---

## 4.2 Script MicroPython (servidor HTTP en Pico W)

### 4.2.1 Propósito
Conectar el microcontrolador a la red WiFi, exponer un endpoint HTTP y devolver el contenido de un archivo local para consumo remoto.

### 4.2.2 Variables de configuración

- `SSID`: nombre de la red WiFi.
- `PASSWORD`: credencial de acceso.
- `ARCHIVO_DATOS = 'datos.txt'`: archivo fuente a publicar.

### 4.2.3 Funciones

- `conectar_wifi()`:
  - Activa interfaz WiFi en modo estación (`STA_IF`).
  - Ejecuta proceso de conexión y espera hasta `isconnected()`.
  - Obtiene y retorna la IP asignada.

- `leer_archivo(nombre)`:
  - Abre el archivo en modo lectura.
  - Retorna contenido completo.
  - Si no existe, retorna mensaje de error controlado.

- `iniciar_servidor(ip)`:
  - Crea socket TCP sobre `0.0.0.0:80`.
  - Habilita `SO_REUSEADDR` para reinicios rápidos.
  - Atiende conexiones en bucle.
  - Router simple:
    - Si la petición contiene `GET /archivo`, devuelve 200 con contenido.
    - En otra ruta, devuelve 404.
  - Añade header `Access-Control-Allow-Origin: *` para habilitar peticiones desde navegador.

### 4.2.4 Robustez implementada

- Control de excepciones en bucle de servidor.
- Cierre del socket cliente ante error para evitar fugas de recursos.
- Respuesta 404 para rutas no definidas.

### 4.2.5 Limitaciones actuales

- Sin autenticación ni cifrado HTTPS.
- Parsing HTTP básico por substring.
- Monohilo y atención secuencial de clientes.
- No incorpora timestamp dinámico de actualización del archivo en el propio Pico.

---

## 4.3 Archivo de datos (`datos.txt`)

### 4.3.1 Propósito
Actuar como fuente de telemetría simulada del sistema PicoW para pruebas de visualización.

### 4.3.2 Estructura observada

- Encabezado del sistema.
- Métricas:
  - Temperatura CPU.
  - Humedad.
  - Voltaje.
- Estado de red WiFi + IP.
- Estado de sensores (PIR, luz, temperatura).
- Marca de última actualización.
- Sección de logs operativos.

### 4.3.3 Valor didáctico

Este formato facilita:
- Pruebas de lectura de archivos de texto plano.
- Validación de render línea por línea.
- Simulación de bitácora técnica de un nodo IoT.

---

## 5) Mapeo con la consigna 4.6

La solución cumple los elementos solicitados:

- **“Elabore un WebServer MicroPython y/o C++ en Raspberry PicoW/Pico2W via Wokwi”**  
  ✅ Se implementa servidor HTTP funcional en **MicroPython** para Pico W.

- **“Interfaz objetivo-ficticia sobre monitoreo del mundo real”**  
  ✅ La UI representa una consola de supervisión de variables ambientales y estado del nodo.

- **“Intervenga UIX de html-css-js dentro de micropython”**  
  ✅ Integración completa entre frontend web y backend embebido mediante endpoint `/archivo`.

- **“Tema abierto y no repetido”**  
  ✅ Tema propuesto: monitoreo ambiental/estado IoT con bitácora del sistema.

---

## 6) Evidencia funcional esperada

1. Al iniciar el script MicroPython, en consola debe mostrarse la IP del Pico.
2. Al abrir la web e ingresar dicha IP, `Fetch Data` debe cargar el contenido de `datos.txt`.
3. Al activar `Auto-refresh`, la vista se actualiza cada 2 segundos.
4. Si IP o red fallan, se muestra error de conexión controlado en el visor.

---

## 7) Recomendaciones de mejora (iteración futura)

1. **Seguridad:** token simple o autenticación básica para endpoint.
2. **Estructura de datos:** migrar a JSON para parsing semántico por campos.
3. **Múltiples endpoints:** `/health`, `/metrics`, `/logs`.
4. **Persistencia y timestamp real:** actualizar `datos.txt` automáticamente desde sensores.
5. **Optimización de red:** cache-control y respuestas diferenciales.
6. **Escalabilidad:** servidor asíncrono (`uasyncio`) en lugar de loop bloqueante.

---

## 8) Conclusión

El proyecto implementa exitosamente un esquema IoT de monitoreo con servidor embebido en Pico W y panel web de visualización, cumpliendo el enfoque de interfaz objetivo-ficticia con bases técnicas reales. La solución es funcional, demostrable en Wokwi y extensible hacia un sistema de telemetría más robusto en escenarios académicos o prototipos de campo.


