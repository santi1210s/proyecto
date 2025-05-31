import sqlite3
from werkzeug.security import generate_password_hash
import json

def crear_base_datos():
    """Crear la base de datos y las tablas necesarias"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Crear tabla usuarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('profesor', 'estudiante'))
    )
    ''')
    
    # Crear tabla estudiantes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS estudiantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL
    )
    ''')
    
    # Crear tabla notas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estudiante_id INTEGER NOT NULL,
        asignatura TEXT NOT NULL,
        nota REAL NOT NULL,
        fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de datos y tablas creadas correctamente.")

def crear_usuarios_iniciales():
    """Crear usuarios iniciales del sistema"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Eliminar usuarios existentes para empezar limpio
    cursor.execute('DELETE FROM usuarios')
    
    # Insertar usuarios con contraseñas hasheadas
    usuarios = [
        ('profesor1', generate_password_hash('admin123'), 'profesor'),
        ('estudiante1', generate_password_hash('alumno123'), 'estudiante'),
        # Agregar algunos estudiantes adicionales basados en el JSON
        ('10A001', generate_password_hash('estudiante123'), 'estudiante'),
        ('10A002', generate_password_hash('estudiante123'), 'estudiante'),
        ('10A003', generate_password_hash('estudiante123'), 'estudiante'),
    ]
    
    cursor.executemany('INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)', usuarios)
    
    conn.commit()
    conn.close()
    print("✅ Usuarios creados correctamente.")

def sincronizar_estudiantes_json():
    """Sincronizar estudiantes del archivo JSON con la base de datos"""
    try:
        with open('estudiantes.json', 'r', encoding='utf-8') as f:
            estudiantes_json = json.load(f)
    except FileNotFoundError:
        print("❌ Archivo estudiantes.json no encontrado")
        return
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    for estudiante in estudiantes_json:
        cursor.execute('''
        INSERT OR IGNORE INTO estudiantes (codigo, nombre) VALUES (?, ?)
        ''', (estudiante['id'], estudiante['nombre']))
    
    conn.commit()
    conn.close()
    print("✅ Estudiantes sincronizados desde JSON.")

if __name__ == '__main__':
    crear_base_datos()
    crear_usuarios_iniciales()
    sincronizar_estudiantes_json()
    print("\n🎉 Configuración de base de datos completada.")
    print("\nCredenciales de acceso:")
    print("Profesor: usuario='profesor1', contraseña='admin123'")
    print("Estudiante: usuario='estudiante1', contraseña='alumno123'")
