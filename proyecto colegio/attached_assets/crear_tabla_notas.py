import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear tabla 'notas' si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER NOT NULL,
    asignatura TEXT NOT NULL,
    nota REAL NOT NULL,
    FOREIGN KEY (estudiante_id) REFERENCES usuarios (id)
)
''')

conn.commit()
conn.close()

print("✅ Tabla 'notas' creada correctamente.")
