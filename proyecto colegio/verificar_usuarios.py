#!/usr/bin/env python3
import sqlite3
from werkzeug.security import check_password_hash

# Conectar a la base de datos
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Verificar usuarios existentes
cursor.execute('SELECT username, password, rol FROM usuarios')
usuarios = cursor.fetchall()

print("Usuarios en la base de datos:")
for username, password_hash, rol in usuarios:
    print(f"- Usuario: {username}, Rol: {rol}")
    
    # Verificar las contraseñas
    if username == 'profesor1':
        password_check = check_password_hash(password_hash, 'admin123')
        print(f"  Contraseña 'admin123' válida: {password_check}")
    elif username == 'estudiante1':
        password_check = check_password_hash(password_hash, 'alumno123')
        print(f"  Contraseña 'alumno123' válida: {password_check}")

# Verificar estudiantes
cursor.execute('SELECT codigo, nombre FROM estudiantes LIMIT 5')
estudiantes = cursor.fetchall()

print(f"\nEstudiantes en la base de datos ({len(estudiantes)} primeros):")
for codigo, nombre in estudiantes:
    print(f"- {codigo}: {nombre}")

conn.close()