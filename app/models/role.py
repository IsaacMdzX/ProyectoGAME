from app import db

class Role(db.Model):
    __tablename__ = 'roles'
    
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30))
    
    # Relación con usuarios
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.nombre}>'