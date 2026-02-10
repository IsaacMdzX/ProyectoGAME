from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from app import db
from app.models.models import Producto, Carrito, CarritoItem

carrito_bp = Blueprint('carrito', __name__)

@carrito_bp.route('/carrito')
def ver_carrito():
    return render_template('carrito.html')

@carrito_bp.route('/api/carrito/agregar', methods=['POST'])
@login_required
def agregar_al_carrito():
    try:
        data = request.get_json()
        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad', 1)
        
        print(f"🔍 Intentando agregar producto {producto_id}, cantidad {cantidad}")
        
        # Verificar que el producto existe
        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404
        
        # Obtener o crear carrito del usuario
        carrito = Carrito.query.filter_by(
            usuario_id=current_user.id_usuario, 
            activo=True
        ).first()
        
        if not carrito:
            carrito = Carrito(usuario_id=current_user.id_usuario)
            db.session.add(carrito)
            db.session.flush()
        
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
        
        return jsonify({
            'success': True,
            'message': 'Producto agregado al carrito'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en agregar_al_carrito: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@carrito_bp.route('/api/carrito', methods=['GET'])
@login_required
def obtener_carrito():
    try:
        carrito = Carrito.query.filter_by(
            usuario_id=current_user.id_usuario, 
            activo=True
        ).first()
        
        if not carrito:
            return jsonify({'items': [], 'total': 0, 'count': 0})
        
        items_data = []
        total = 0
        count = 0
        
        for item in carrito.items:
            producto = item.producto
            subtotal = item.cantidad * float(item.precio_unitario)
            total += subtotal
            count += item.cantidad
            
            items_data.append({
                'id': item.id_item,
                'producto_id': producto.id_producto,
                'nombre': producto.nombre,
                'precio': float(item.precio_unitario),
                'cantidad': item.cantidad,
                'imagen': producto.imagen,
                'categoria': producto.categoria.nombre,
                'subtotal': float(subtotal)
            })
        
        return jsonify({
            'items': items_data,
            'total': float(total),
            'count': count
        })
        
    except Exception as e:
        print(f"❌ Error en obtener_carrito: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@carrito_bp.route('/api/carrito/actualizar/<int:item_id>', methods=['PUT'])
@login_required
def actualizar_carrito(item_id):
    try:
        data = request.get_json()
        nueva_cantidad = data.get('cantidad')
        
        item = CarritoItem.query.get_or_404(item_id)
        
        # Verificar que el item pertenezca al usuario
        if item.carrito.usuario_id != current_user.id_usuario:
            return jsonify({'success': False, 'message': 'No autorizado'}), 403
        
        if nueva_cantidad <= 0:
            db.session.delete(item)
            message = 'Producto eliminado del carrito'
        else:
            item.cantidad = nueva_cantidad
            message = 'Cantidad actualizada'
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': message})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@carrito_bp.route('/api/carrito/eliminar/<int:item_id>', methods=['DELETE'])
@login_required
def eliminar_del_carrito(item_id):
    try:
        item = CarritoItem.query.get_or_404(item_id)
        
        # Verificar que el item pertenezca al usuario
        if item.carrito.usuario_id != current_user.id_usuario:
            return jsonify({'success': False, 'message': 'No autorizado'}), 403
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Producto eliminado del carrito'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@carrito_bp.route('/api/productos', methods=['GET'])
def obtener_productos():
    try:
        productos = Producto.query.filter_by(activo=True).all()
        productos_data = []
        
        for producto in productos:
            productos_data.append({
                'id': producto.id_producto,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio': float(producto.precio),
                'stock': producto.stock,
                'imagen': producto.imagen,
                'categoria': producto.categoria.nombre,
                'categoria_id': producto.categoria_id
            })
        
        return jsonify(productos_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500