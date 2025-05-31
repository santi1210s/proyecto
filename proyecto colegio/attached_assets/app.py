from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'clave_supersecreta'

# Simulación de usuarios
usuarios = {
    'profesor1': {'password': '1234', 'rol': 'profesor'},
    'estudiante1': {'password': 'abcd', 'rol': 'estudiante'}
}

# Notas simuladas (en memoria)
notas_guardadas = []

# Leer estudiantes desde archivo JSON
def cargar_estudiantes():
    with open('estudiantes.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in usuarios and usuarios[username]['password'] == password:
        session['username'] = username
        session['rol'] = usuarios[username]['rol']
        if session['rol'] == 'profesor':
            return redirect(url_for('panel_profesor'))
        else:
            return redirect(url_for('panel_estudiante'))
    return 'Usuario o contraseña incorrectos'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/panel_profesor')
def panel_profesor():
    if 'username' not in session or session['rol'] != 'profesor':
        return redirect(url_for('index'))
    estudiantes = cargar_estudiantes()
    return render_template('panel_profesor.html', username=session['username'], notas=notas_guardadas, estudiantes=estudiantes)

@app.route('/agregar_nota', methods=['POST'])
def agregar_nota():
    id_estudiante = request.form['id_estudiante']
    asignatura = request.form['asignatura']
    nota = request.form['nota']

    estudiantes = cargar_estudiantes()
    estudiante = next((e for e in estudiantes if e['id'] == id_estudiante), None)

    nueva_nota = {
        'estudiante': estudiante['nombre'] if estudiante else id_estudiante,
        'asignatura': asignatura,
        'nota': nota
    }

    notas_guardadas.append(nueva_nota)
    return redirect(url_for('panel_profesor'))

@app.route('/panel_estudiante')
def panel_estudiante():
    return 'Panel para el estudiante (próximamente...)'

if __name__ == '__main__':
    app.run(debug=True)
