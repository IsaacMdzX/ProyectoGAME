from datetime import datetime
from app import db


class AdminActivity(db.Model):
    __tablename__ = 'admin_activity'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # ejemplo: producto, pedido, usuario, sistema
    descripcion = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=True)
    referencia_tipo = db.Column(db.String(50))
    referencia_id = db.Column(db.Integer)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class InventarioMovimiento(db.Model):
    __tablename__ = 'inventario_movimientos'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # entrada | salida | ajuste
    cantidad = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(200))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Pago(db.Model):
    __tablename__ = 'pagos'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'), nullable=False)
    proveedor = db.Column(db.String(30), nullable=False)  # paypal | mercadopago
    estado = db.Column(db.String(30), nullable=False)  # pendiente | aprobado | rechazado
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    moneda = db.Column(db.String(10), default='USD')
    referencia = db.Column(db.String(255))
    payload = db.Column(db.JSON)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Reporte(db.Model):
    __tablename__ = 'reportes'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # ventas, inventario, clientes, etc
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    estado = db.Column(db.String(20), default='completado')
    total = db.Column(db.Numeric(12, 2))
    metadata_json = db.Column(db.JSON)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    generado_en = db.Column(db.DateTime)


class ReporteItem(db.Model):
    __tablename__ = 'reporte_items'

    id = db.Column(db.Integer, primary_key=True)
    reporte_id = db.Column(db.Integer, db.ForeignKey('reportes.id'), nullable=False)
    clave = db.Column(db.String(100), nullable=False)
    valor_texto = db.Column(db.String(255))
    valor_numero = db.Column(db.Numeric(12, 2))
    orden = db.Column(db.Integer, default=0)

    reporte = db.relationship('Reporte', backref=db.backref('items', lazy=True, cascade='all, delete-orphan'))
