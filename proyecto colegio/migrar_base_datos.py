#!/usr/bin/env python3
import sqlite3
import json

def migrar_base_datos():
    """Migrar la base de datos para agregar las nuevas columnas"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Verificar si las columnas ya existen
    cursor.execute("PRAGMA table_info(usuarios)")
    columnas = [row[1] for row in cursor.fetchall()]
    
    # Agregar columna nombre_completo si no existe
    if 'nombre_completo' not in columnas:
        cursor.execute('ALTER TABLE usuarios ADD COLUMN nombre_completo TEXT')
        print("✅ Columna 'nombre_completo' agregada")
    
    # Agregar columna materias si no existe
    if 'materias' not in columnas:
        cursor.execute('ALTER TABLE usuarios ADD COLUMN materias TEXT')
        print("✅ Columna 'materias' agregada")
    
    # Actualizar datos de profesores con información adicional
    materias_matematicas = json.dumps(["Matemáticas", "Álgebra", "Geometría"])
    materias_ciencias = json.dumps(["Ciencias Naturales", "Física", "Química"])
    materias_humanidades = json.dumps(["Español", "Ciencias Sociales", "Inglés"])
    
    # Actualizar profesor1 con nombre y materias
    cursor.execute('''
        UPDATE usuarios 
        SET nombre_completo = ?, materias = ? 
        WHERE username = ? AND rol = ?
    ''', ("Oscar Martínez", materias_matematicas, "profesor1", "profesor"))
    
    # Crear más profesores de ejemplo
    profesores_adicionales = [
        ("profesor2", "admin123", "María González", materias_ciencias),
        ("profesor3", "admin123", "Carlos Rodríguez", materias_humanidades)
    ]
    
    from werkzeug.security import generate_password_hash
    
    for username, password, nombre, materias in profesores_adicionales:
        cursor.execute('''
            INSERT OR IGNORE INTO usuarios (username, password, rol, nombre_completo, materias)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, generate_password_hash(password), "profesor", nombre, materias))
    
    conn.commit()
    conn.close()
    print("🎉 Migración completada exitosamente")

if __name__ == '__main__':
    migrar_base_datos()