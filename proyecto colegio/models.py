from app import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
    
    def get_nombre_completo(self):
        """Obtener nombre completo basado en el username"""
        if self.username == 'profesor1':
            return 'Oscar Martínez'
        return self.username.title()
    
    def get_materias(self):
        """Obtener lista de materias del profesor"""
        if self.rol == 'profesor' and self.username == 'profesor1':
            return ["Matemáticas", "Álgebra", "Geometría"]
        return []

class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    
    # Relación con notas
    notas = db.relationship('Nota', backref='estudiante', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Estudiante {self.codigo} - {self.nombre}>'
    
    def promedio_general(self):
        """Calcular el promedio general del estudiante"""
        if not self.notas:
            return 0
        return sum(nota.nota for nota in self.notas) / len(self.notas)

class Nota(db.Model):
    __tablename__ = 'notas'
    
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id'), nullable=False)
    asignatura = db.Column(db.String(100), nullable=False)
    nota = db.Column(db.Float, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Nota {self.asignatura}: {self.nota}>'
    
    def estado(self):
        """Determinar si la nota es aprobatoria"""
        return "Aprobado" if self.nota >= 6.0 else "Reprobado"
