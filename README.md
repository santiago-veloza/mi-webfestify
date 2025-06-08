📝Descripción del proyecto

Festify es una plataforma web desarrollada con Flask que permite la gestión y compra de tiquetes para eventos.
El sistema está dividido en dos tipos de usuarios: administradores (usuarios normales) y clientes.

Funciones principales:

Administradores pueden crear, editar y eliminar eventos, especificando detalles como nombre, fecha, hora, ubicación, precio y cantidad de tiquetes disponibles.

Clientes pueden registrarse, iniciar sesión y ver los eventos disponibles para comprar tiquetes.

Cada cliente puede comprar múltiples tiquetes para un evento, respetando la cantidad disponible.

El sistema registra cada compra en una tabla especial (compras) que almacena qué cliente compró, cuántos tiquetes y para qué evento.

Se integró el envío de correos electrónicos automáticos al registrarse, informando al usuario o cliente que su registro fue exitoso.

El diseño de la web es moderno, amigable y presenta los eventos en tarjetas (cuadritos) para mejorar la visualización.

Se utiliza MariaDB como base de datos, aplicando buenas prácticas de conexión y consultas.

Se usan mensajes flash para notificar al usuario de errores, advertencias o confirmaciones de manera clara.

🔥 Tecnologías utilizadas

Python 3 + Flask (framework web)

MariaDB (base de datos relacional)

HTML5, CSS3 (Frontend personalizado)

Flask-WTF para formularios seguros

Flask-Mail para envío de correos

Werkzeug para manejo seguro de contraseñas


Crear y activar un entorno virtual (recomendado para manejar dependencias):

En Windows PowerShell:

powershell
Copiar
python -m venv venv
.\venv\Scripts\Activate.ps1
En Linux/macOS:

bash
Copiar
python3 -m venv venv
source venv/bin/activate
Instalar las dependencias:

bash
Copiar
pip install -r requirements.txt
Configurar las variables de entorno para Flask (en PowerShell):

powershell
Copiar
$env:FLASK_APP = 'run'
$env:FLASK_ENV = 'development'
$env:FLASK_DEBUG = '1'
Ejecutar la aplicación:

Si no estás ya dentro del directorio festify, entra:

powershell
Copiar
cd festify
Luego inicia el servidor Flask:

bash
Copiar
flask run --host=0.0.0.0
Abrir la aplicación en el navegador:

Accede a http://127.0.0.1:5000 o a la IP que aparezca en consola para usar la aplicación.




