from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from app.models.models import Carrito, CarritoItem, Producto
from app import db

bp = Blueprint('carrito_api', __name__)

@bp.route('/api/carrito', methods=['GET'])
@login_required
def obtener_carrito():
    try:
        carrito = Carrito.query.filter_by(usuario_id=current_user.id_usuario, activo=True).first()
        
        if not carrito:
            return jsonify({'items': [], 'total': 0})
        
        items = CarritoItem.query.filter_by(carrito_id=carrito.id_carrito).all()
        
        items_data = []
        total = 0
        
        for item in items:
            producto = Producto.query.get(item.producto_id)
            if producto:
                subtotal = item.cantidad * item.precio_unitario
                total += subtotal
                
                items_data.append({
                    'id_item': item.id_item,
                    'producto_id': item.producto_id,
                    'nombre': producto.nombre,
                    'precio_unitario': float(item.precio_unitario),
                    'cantidad': item.cantidad,
                    'imagen': producto.imagen,
                    'subtotal': float(subtotal)
                })
        
        return jsonify({
            'items': items_data,
            'total': float(total)
        })
        
    except Exception as e:
        print(f"Error en obtener_carrito: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/api/carrito/agregar', methods=['POST'])
@login_required
def agregar_al_carrito():
    try:
        data = request.get_json()
        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad', 1)
        
        if not producto_id:
            return jsonify({'error': 'ID de producto requerido'}), 400
        
        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Obtener o crear carrito
        carrito = Carrito.query.filter_by(usuario_id=current_user.id_usuario, activo=True).first()
        if not carrito:
            carrito = Carrito(usuario_id=current_user.id_usuario)
            db.session.add(carrito)
            db.session.commit()
        
        # Verificar si el producto ya está en el carrito
        item_existente = CarritoItem.query.filter_by(
            carrito_id=carrito.id_carrito, 
            producto_id=producto_id
        ).first()
        
        if item_existente:
            item_existente.cantidad += cantidad
        else:
            nuevo_item = CarritoItem(
                carrito_id=carrito.id_carrito,
                producto_id=producto_id,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            db.session.add(nuevo_item)
        
        db.session.commit()
        
        return jsonify({'mensaje': 'Producto agregado al carrito'})
        
    except Exception as e:
        print(f"Error en agregar_al_carrito: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/api/carrito/items/<int:item_id>', methods=['PUT'])
@login_required
def actualizar_item_carrito(item_id):
    try:
        data = request.get_json()
        cambio = data.get('cambio', 0)
        
        item = CarritoItem.query.get(item_id)
        if not item:
            return jsonify({'error': 'Item no encontrado'}), 404
        
        # Verificar que el item pertenezca al usuario
        carrito = Carrito.query.get(item.carrito_id)
        if carrito.usuario_id != current_user.id_usuario:
            return jsonify({'error': 'No autorizado'}), 403
        
        nueva_cantidad = item.cantidad + cambio
        
        if nueva_cantidad <= 0:
            db.session.delete(item)
        else:
            item.cantidad = nueva_cantidad
        
        db.session.commit()
        
        return jsonify({'mensaje': 'Carrito actualizado'})
        
    except Exception as e:
        print(f"Error en actualizar_item_carrito: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/api/carrito/items/<int:item_id>', methods=['DELETE'])
@login_required
def eliminar_item_carrito(item_id):
    try:
        item = CarritoItem.query.get(item_id)
        if not item:
            return jsonify({'error': 'Item no encontrado'}), 404
        
        # Verificar que el item pertenezca al usuario
        carrito = Carrito.query.get(item.carrito_id)
        if carrito.usuario_id != current_user.id_usuario:
            return jsonify({'error': 'No autorizado'}), 403
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'mensaje': 'Item eliminado del carrito'})
        
    except Exception as e:
        print(f"Error en eliminar_item_carrito: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/api/carrito/cantidad', methods=['GET'])
def obtener_cantidad_carrito():
    try:
        if not current_user.is_authenticated:
            return jsonify({'cantidad': 0})
        
        carrito = Carrito.query.filter_by(usuario_id=current_user.id_usuario, activo=True).first()
        if not carrito:
            return jsonify({'cantidad': 0})
        
        cantidad_total = db.session.query(db.func.sum(CarritoItem.cantidad))\
            .filter(CarritoItem.carrito_id == carrito.id_carrito)\
            .scalar() or 0
        
        return jsonify({'cantidad': cantidad_total})
        
    except Exception as e:
        print(f"Error en obtener_cantidad_carrito: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500