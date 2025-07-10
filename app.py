from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_pymongo import PyMongo
from functools import wraps
import os
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
import re
import time
import logging
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

load_dotenv()

# Configuración de MongoDB Atlas (ahora desde variables de entorno)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)
app.secret_key = os.getenv('SECRET_KEY', 'caninexpress-super-secreto')

# Credenciales admin desde variables de entorno
ADMIN_USER = os.getenv('ADMIN_USER', 'caninexpress')
ADMIN_PASS_HASH = os.getenv('ADMIN_PASS_HASH')

# Validar configuración crítica
if not app.config["MONGO_URI"]:
    raise RuntimeError("Falta la variable de entorno MONGO_URI")
if not ADMIN_PASS_HASH:
    raise RuntimeError("Falta la variable de entorno ADMIN_PASS_HASH (hash de la contraseña de admin)")

# Configuración de Cloudinary
cloudinary.config(
  cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
  api_key = os.getenv('CLOUDINARY_API_KEY'),
  api_secret = os.getenv('CLOUDINARY_API_SECRET')
)

# Decorador para requerir login
def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if not session.get('admin_logueado'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorada

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

# Modificar login para usar la colección usuarios
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logueado'):
        return redirect(url_for('admin'))
    error = None
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        if mongo.db is None:
            error = 'Base de datos no disponible.'
        else:
            user_doc = mongo.db.usuarios.find_one({'usuario': usuario})
            if user_doc and user_doc.get('password') and check_password_hash(user_doc['password'], password):
                session['admin_logueado'] = True
                session['usuario'] = usuario
                session['rol'] = user_doc.get('rol', 'editor')
                return redirect(url_for('admin'))
            else:
                error = 'Usuario o contraseña incorrectos.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('admin_logueado', None)
    return redirect(url_for('login'))

@app.route('/admin')
@login_requerido
def admin():
    return render_template('admin.html')

@app.route('/api/productos', methods=['GET'])
def api_get_productos():
    if mongo.db is None:
        return jsonify({'error': 'Base de datos no disponible'}), 500
    productos = list(mongo.db.productos.find({}, {'_id': 0}))
    return jsonify(productos)

@app.route('/api/productos', methods=['POST'])
@login_requerido
def api_add_producto():
    if mongo.db is None:
        return jsonify({'error': 'Base de datos no disponible'}), 500
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    img = data.get('img', '').strip()
    desc = data.get('desc', '').strip()
    errores = []
    if not (nombre and img and desc is not None):
        errores.append('Faltan campos')
    if len(nombre) < 2 or len(nombre) > 40:
        errores.append('El nombre debe tener entre 2 y 40 caracteres.')
    # Quitar la validación de longitud mínima para desc
    if len(desc) > 300:
        errores.append('La descripción debe tener como máximo 300 caracteres.')
    if errores:
        return jsonify({'error': ' | '.join(errores)}), 400
    mongo.db.productos.insert_one({'nombre': nombre, 'img': img, 'desc': desc})
    return jsonify({'ok': True})

@app.route('/api/productos', methods=['DELETE'])
@login_requerido
def api_delete_producto():
    if mongo.db is None:
        return jsonify({'error': 'Base de datos no disponible'}), 500
    data = request.get_json()
    nombre = data.get('nombre')
    if not nombre:
        return jsonify({'error': 'Falta el nombre'}), 400
    mongo.db.productos.delete_one({'nombre': nombre})
    return jsonify({'ok': True})

@app.route('/api/productos', methods=['PUT'])
@login_requerido
def api_edit_producto():
    if mongo.db is None:
        return jsonify({'error': 'Base de datos no disponible'}), 500
    data = request.get_json()
    nombre = data.get('nombre')
    nuevo = data.get('nuevo')
    if not (nombre and nuevo):
        return jsonify({'error': 'Faltan datos'}), 400
    mongo.db.productos.update_one({'nombre': nombre}, {'$set': nuevo})
    return jsonify({'ok': True})

@app.route('/api/upload_img', methods=['POST'])
@login_requerido
def upload_img():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        # Subir a Cloudinary
        result = cloudinary.uploader.upload(file, folder="canin_express")
        url = result.get('secure_url')
        return jsonify({'url': url})
    return jsonify({'error': 'Tipo de archivo no permitido'}), 400

@app.route('/contacto', methods=['POST'])
def contacto():
    nombre = request.form.get('nombre', '').strip()
    email = request.form.get('email', '').strip()
    mensaje = request.form.get('mensaje', '').strip()
    errores = []
    if not (nombre and email and mensaje):
        errores.append('Por favor, completa todos los campos.')
    if len(nombre) < 2 or len(nombre) > 40:
        errores.append('El nombre debe tener entre 2 y 40 caracteres.')
    email_regex = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    if not re.match(email_regex, email):
        errores.append('El correo electrónico no es válido.')
    if len(mensaje) < 10 or len(mensaje) > 500:
        errores.append('El mensaje debe tener entre 10 y 500 caracteres.')
    if errores:
        flash(' '.join(errores), 'error')
        return redirect(url_for('index') + '#contacto')
    # Configuración de email ahora desde variables de entorno
    remitente = os.getenv('EMAIL_USER', 'caninexpresss@gmail.com')
    destinatario = os.getenv('EMAIL_DEST', 'caninexpresss@gmail.com')
    asunto = f'Nuevo mensaje de contacto de {nombre}'
    cuerpo = f"""
    Nombre: {nombre}\nEmail: {email}\nMensaje:\n{mensaje}
    """
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain'))
    if not os.getenv('EMAIL_PASS'):
        flash('Error de configuración: falta EMAIL_PASS en el servidor.', 'error')
        return redirect(url_for('index') + '#contacto')
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(remitente, str(os.getenv('EMAIL_PASS')))
            server.sendmail(remitente, destinatario, msg.as_string())
        flash('¡Mensaje enviado correctamente! Te responderemos pronto 😊', 'success')
    except Exception as e:
        flash('Ocurrió un error al enviar el mensaje. Intenta nuevamente más tarde.', 'error')
    return redirect(url_for('index') + '#contacto')

# --- Gestión de usuarios y roles ---
# Solo el primer usuario admin se crea manualmente en la base. El resto se gestiona desde el panel.

@app.route('/admin/usuarios', methods=['GET'])
@login_requerido
def listar_usuarios():
    if mongo.db is None:
        return 'Base de datos no disponible', 500
    usuario = session.get('usuario')
    user_doc = mongo.db.usuarios.find_one({'usuario': usuario})
    if not user_doc or user_doc.get('rol') != 'admin':
        return 'No autorizado', 403
    usuarios = list(mongo.db.usuarios.find({}, {'_id': 0, 'password': 0}))
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/admin/usuarios/registrar', methods=['POST'])
@login_requerido
def registrar_usuario():
    if mongo.db is None:
        return 'Base de datos no disponible', 500
    usuario = session.get('usuario')
    user_doc = mongo.db.usuarios.find_one({'usuario': usuario})
    if not user_doc or user_doc.get('rol') != 'admin':
        return 'No autorizado', 403
    data = request.form
    nuevo_usuario = data.get('usuario')
    password = data.get('password')
    rol = data.get('rol', 'editor')
    if not (nuevo_usuario and password):
        flash('Faltan datos', 'error')
        return redirect(url_for('listar_usuarios'))
    if mongo.db.usuarios.find_one({'usuario': nuevo_usuario}):
        flash('El usuario ya existe', 'error')
        return redirect(url_for('listar_usuarios'))
    hash_pw = generate_password_hash(password)
    mongo.db.usuarios.insert_one({'usuario': nuevo_usuario, 'password': hash_pw, 'rol': rol})
    flash('Usuario creado correctamente', 'success')
    return redirect(url_for('listar_usuarios'))

# Configurar logging para errores críticos
logging.basicConfig(filename='errores.log', level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')

# Manejo global de errores
@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('error.html', mensaje='Página no encontrada (404)'), 404

@app.errorhandler(500)
def error_interno(e):
    logging.error(f'Error interno: {e}')
    return render_template('error.html', mensaje='Ocurrió un error interno. Intenta más tarde o contacta al administrador.'), 500

if __name__ == '__main__':
    print('\nTu app está corriendo en: http://127.0.0.1:5000/')
    app.run(debug=True) 