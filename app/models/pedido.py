from app import db
from datetime import datetime

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id_pedido = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(50), default='pendiente')
    direccion_envio = db.Column(db.Text)
    metodo_pago = db.Column(db.String(50), default='paypal')  # ✅ AGREGAR ESTA LÍNEA
    id_transaccion_paypal = db.Column(db.String(255))
    id_transaccion_mercadopago = db.Column(db.String(255))
    
    # Relaciones
    usuario = db.relationship('Usuario', backref=db.backref('pedidos', lazy=True))
    items = db.relationship('PedidoItem', backref='pedido', lazy=True, cascade='all, delete-orphan')

class PedidoItem(db.Model):
    __tablename__ = 'pedido_items'
    id_item = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'))
    cantidad = db.Column(db.Integer, default=1)
    precio_unitario = db.Column(db.Numeric(10, 2))
    
    producto = db.relationship('Producto', backref='pedido_items')