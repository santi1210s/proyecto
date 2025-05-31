import sqlite3
from werkzeug.security import generate_password_hash

# Conectar a la base de datos
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear tabla 'usuarios' si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('profesor', 'estudiante'))
)
''')

# Eliminar usuarios existentes (opcional si quieres empezar limpio)
cursor.execute('DELETE FROM usuarios')

# Insertar usuarios con contraseñas hasheadas
usuarios = [
    ('profesor1', generate_password_hash('admin123'), 'profesor'),
    ('estudiante1', generate_password_hash('alumno123'), 'estudiante')
]

cursor.executemany('INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)', usuarios)

# Confirmar y cerrar
conn.commit()
conn.close()

print("✅ Usuarios creados correctamente.")
