from app import db
from flask_login import UserMixin
from datetime import datetime

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    productos = db.relationship('Producto', backref='categoria', lazy=True)

class Producto(db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    imagen = db.Column(db.String(500))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'))
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

class Carrito(db.Model):
    __tablename__ = 'carrito'
    id_carrito = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    usuario = db.relationship('Usuario', backref='carritos')
    items = db.relationship('CarritoItem', backref='carrito', lazy=True, cascade='all, delete-orphan')

class CarritoItem(db.Model):
    __tablename__ = 'carrito_items'
    id_item = db.Column(db.Integer, primary_key=True)
    carrito_id = db.Column(db.Integer, db.ForeignKey('carrito.id_carrito'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'))
    cantidad = db.Column(db.Integer, default=1)
    precio_unitario = db.Column(db.Numeric(10, 2))
    fecha_agregado = db.Column(db.DateTime, default=datetime.utcnow)
    
    producto = db.relationship('Producto', backref='carrito_items')
    