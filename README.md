# Canin Express

Tienda de forrajería y artículos para mascotas, con panel de administración y catálogo online.

## Características
- Catálogo de productos dinámico
- Panel de administración seguro (gestión de productos y usuarios)
- Formulario de contacto con envío de email
- Imágenes y diseño moderno

## Instalación local

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tuusuario/canin-express.git
   cd canin-express
   ```
2. Crea un entorno virtual y activa:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   # o
   source venv/bin/activate  # En Linux/Mac
   ```
3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Copia `.env.example` a `.env` y completa tus datos reales.

5. Ejecuta la app:
   ```bash
   python app.py
   ```

## Variables de entorno
Configura un archivo `.env` con:
```
MONGO_URI=tu_uri_de_mongodb
SECRET_KEY=tu_clave_secreta
ADMIN_USER=admin
ADMIN_PASS_HASH=hash_generado
EMAIL_USER=tu_email@gmail.com
EMAIL_PASS=contraseña_de_aplicacion_gmail
EMAIL_DEST=tu_email@gmail.com
```

## Despliegue en Render
- Sube el repo a GitHub.
- En Render, crea un nuevo Web Service y conecta tu repo.
- Usa el comando de arranque:
  ```
  gunicorn app:app
  ```
- Agrega las variables de entorno en el panel de Render.

---

¡Hecho con �� y pasión animal! 