#!/usr/bin/env python3
import sqlite3
import json
from werkzeug.security import generate_password_hash

def crear_base_datos_nueva():
    """Crear una nueva base de datos con la estructura completa"""
    # Eliminar base de datos existente
    import os
    if os.path.exists('database.db'):
        os.remove('database.db')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Crear tabla usuarios con todas las columnas
    cursor.execute('''
    CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('profesor', 'estudiante')),
        nombre_completo TEXT,
        materias TEXT
    )
    ''')
    
    # Crear tabla estudiantes
    cursor.execute('''
    CREATE TABLE estudiantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL
    )
    ''')
    
    # Crear tabla notas
    cursor.execute('''
    CREATE TABLE notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estudiante_id INTEGER NOT NULL,
        asignatura TEXT NOT NULL,
        nota REAL NOT NULL,
        fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id)
    )
    ''')
    
    # Insertar usuarios iniciales
    materias_oscar = json.dumps(["Matemáticas", "Álgebra", "Geometría"])
    
    usuarios = [
        ('profesor1', generate_password_hash('admin123'), 'profesor', 'Oscar Martínez', materias_oscar),
        ('estudiante1', generate_password_hash('alumno123'), 'estudiante', None, None)
    ]
    
    cursor.executemany('''
        INSERT INTO usuarios (username, password, rol, nombre_completo, materias) 
        VALUES (?, ?, ?, ?, ?)
    ''', usuarios)
    
    # Insertar estudiantes desde JSON
    try:
        with open('estudiantes.json', 'r', encoding='utf-8') as f:
            estudiantes_data = json.load(f)
            
        for estudiante in estudiantes_data:
            cursor.execute('''
                INSERT INTO estudiantes (codigo, nombre) VALUES (?, ?)
            ''', (estudiante['id'], estudiante['nombre']))
    except FileNotFoundError:
        print("Archivo estudiantes.json no encontrado")
    
    conn.commit()
    conn.close()
    print("✅ Nueva base de datos creada exitosamente")
    print("Credenciales:")
    print("- Profesor: usuario='profesor1', contraseña='admin123'")
    print("- Estudiante: usuario='estudiante1', contraseña='alumno123'")

if __name__ == '__main__':
    crear_base_datos_nueva()