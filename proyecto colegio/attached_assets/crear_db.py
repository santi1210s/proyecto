import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear tabla
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    rol TEXT NOT NULL
)
''')

# Insertar usuarios
usuarios = [
    ('profesor1', generate_password_hash('admin123'), 'profesor'),
    ('estudiante1', generate_password_hash('alumno123'), 'estudiante')
]

cursor.executemany('INSERT OR IGNORE INTO usuarios (username, password, rol) VALUES (?, ?, ?)', usuarios)

conn.commit()
conn.close()

print("Base de datos creada y usuarios insertados correctamente.")
