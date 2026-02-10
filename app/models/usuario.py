from app import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    correo = db.Column(db.String(100), unique=True, nullable=False)
    nombre_usuario = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    ultimo_acceso = db.Column(db.TIMESTAMP, nullable=True)
    telefono = db.Column(db.String(15))
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)
    activo = db.Column(db.Boolean, default=True)  # Este campo ya existe en tu BD
    
    # Para Flask-Login
    def get_id(self):
        return str(self.id_usuario)
    
    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'