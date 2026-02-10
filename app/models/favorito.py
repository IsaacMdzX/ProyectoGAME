# favorito.py - CORREGIR
from app import db
from datetime import datetime

class Favorito(db.Model):
    __tablename__ = 'favoritos'
    
    # CORREGIR: El nombre debe coincidir con la BD
    id_favorito = db.Column(db.Integer, primary_key=True)  # Quitar el primer argumento
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    fecha_agregado = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    usuario = db.relationship('Usuario', backref='favoritos')
    producto = db.relationship('Producto', backref='favoritos')
    
    def __repr__(self):
        return f'<Favorito usuario_id:{self.usuario_id} producto_id:{self.producto_id}>'