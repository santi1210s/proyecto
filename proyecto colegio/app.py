import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "clave_supersecreta_desarrollo")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

# Initialize the app with the extension
db.init_app(app)

# Import models after db initialization
from models import Usuario, Nota, Estudiante

def cargar_estudiantes():
    """Cargar estudiantes desde archivo JSON"""
    try:
        with open('estudiantes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def obtener_saludo():
    """Obtener saludo apropiado según la hora del día"""
    hora_actual = datetime.now().hour
    if 5 <= hora_actual < 12:
        return "Buenos días"
    elif 12 <= hora_actual < 18:
        return "Buenas tardes"
    else:
        return "Buenas noches"

def sincronizar_estudiantes():
    """Sincronizar estudiantes del JSON con la base de datos"""
    estudiantes_json = cargar_estudiantes()
    for estudiante_data in estudiantes_json:
        estudiante_existente = Estudiante.query.filter_by(codigo=estudiante_data['id']).first()
        if not estudiante_existente:
            nuevo_estudiante = Estudiante(
                codigo=estudiante_data['id'],
                nombre=estudiante_data['nombre']
            )
            db.session.add(nuevo_estudiante)
    db.session.commit()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    usuario = Usuario.query.filter_by(username=username).first()
    
    if usuario and check_password_hash(usuario.password, password):
        session['user_id'] = usuario.id
        session['username'] = usuario.username
        session['rol'] = usuario.rol
        
        if usuario.rol == 'profesor':
            return redirect(url_for('panel_profesor'))
        else:
            return redirect(url_for('panel_estudiante'))
    else:
        flash('Usuario o contraseña incorrectos', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('index'))

@app.route('/panel_profesor')
def panel_profesor():
    if 'user_id' not in session or session['rol'] != 'profesor':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    # Obtener información del profesor
    profesor = Usuario.query.get(session['user_id'])
    saludo = obtener_saludo()
    
    estudiantes = Estudiante.query.all()
    notas = Nota.query.join(Estudiante).all()
    
    # Filtrar notas por materias del profesor si tiene materias asignadas
    materias_profesor = profesor.get_materias() if profesor else []
    if materias_profesor:
        notas = [nota for nota in notas if nota.asignatura in materias_profesor]
    
    return render_template('panel_profesor.html', 
                         username=session['username'],
                         profesor=profesor,
                         saludo=saludo,
                         estudiantes=estudiantes, 
                         notas=notas,
                         materias_profesor=materias_profesor)

@app.route('/agregar_nota', methods=['POST'])
def agregar_nota():
    if 'user_id' not in session or session['rol'] != 'profesor':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    estudiante_codigo = request.form['estudiante_codigo']
    asignatura = request.form['asignatura']
    nota_valor = request.form['nota']
    
    try:
        nota_valor = float(nota_valor)
        if nota_valor < 1 or nota_valor > 10:
            flash('La nota debe estar entre 1 y 10', 'error')
            return redirect(url_for('panel_profesor'))
    except ValueError:
        flash('Valor de nota inválido', 'error')
        return redirect(url_for('panel_profesor'))
    
    estudiante = Estudiante.query.filter_by(codigo=estudiante_codigo).first()
    if not estudiante:
        flash('Estudiante no encontrado', 'error')
        return redirect(url_for('panel_profesor'))
    
    nueva_nota = Nota(
        estudiante_id=estudiante.id,
        asignatura=asignatura,
        nota=nota_valor
    )
    
    db.session.add(nueva_nota)
    db.session.commit()
    
    flash('Nota agregada correctamente', 'success')
    return redirect(url_for('panel_profesor'))

@app.route('/eliminar_nota/<int:nota_id>')
def eliminar_nota(nota_id):
    if 'user_id' not in session or session['rol'] != 'profesor':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    nota = Nota.query.get_or_404(nota_id)
    db.session.delete(nota)
    db.session.commit()
    
    flash('Nota eliminada correctamente', 'success')
    return redirect(url_for('panel_profesor'))

@app.route('/panel_estudiante')
def panel_estudiante():
    if 'user_id' not in session or session['rol'] != 'estudiante':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    # Para estudiantes, mostrar solo sus propias notas
    # En este caso, asumimos que el username del estudiante corresponde al código
    usuario = Usuario.query.get(session['user_id'])
    estudiante = Estudiante.query.filter_by(codigo=usuario.username).first()
    
    if estudiante:
        mis_notas = Nota.query.filter_by(estudiante_id=estudiante.id).all()
        return render_template('panel_estudiante.html', 
                             username=session['username'],
                             estudiante=estudiante,
                             notas=mis_notas)
    else:
        flash('Perfil de estudiante no encontrado', 'error')
        return render_template('panel_estudiante.html', 
                             username=session['username'],
                             estudiante=None,
                             notas=[])

# Initialize database and create users
def inicializar_base_datos():
    """Inicializar la base de datos y crear usuarios si no existen"""
    with app.app_context():
        db.create_all()
        
        # Verificar si existen usuarios, si no, crearlos
        try:
            count = Usuario.query.count()
        except:
            count = 0
            
        if count == 0:
            from werkzeug.security import generate_password_hash
            import json
            
            # Crear usuarios iniciales básicos
            profesor = Usuario(
                username='profesor1',
                password=generate_password_hash('admin123'),
                rol='profesor'
            )
            estudiante = Usuario(
                username='estudiante1', 
                password=generate_password_hash('alumno123'),
                rol='estudiante'
            )
            
            db.session.add(profesor)
            db.session.add(estudiante)
            db.session.commit()
            
        sincronizar_estudiantes()

# Inicializar cuando se importe el módulo
inicializar_base_datos()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
