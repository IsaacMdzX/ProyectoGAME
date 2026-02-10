from flask import Blueprint, request, jsonify
from app.models.models import Producto, Categoria
from app import db

bp = Blueprint('productos_api', __name__)

@bp.route('/api/productos', methods=['GET'])
def obtener_productos():
    try:
        categoria_nombre = request.args.get('categoria', 'Todos')
        buscar = request.args.get('buscar', '')
        
        # Consulta base con join
        query = db.session.query(Producto, Categoria).join(Categoria)
        
        if categoria_nombre != 'Todos':
            query = query.filter(Categoria.nombre == categoria_nombre)
        
        if buscar:
            query = query.filter(Producto.nombre.ilike(f'%{buscar}%'))
        
        # Filtrar solo productos activos
        query = query.filter(Producto.activo == True)
        
        resultados = query.all()
        
        productos_data = []
        for producto, categoria in resultados:
            productos_data.append({
                'id_producto': producto.id_producto,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio': float(producto.precio),
                'stock': producto.stock,
                'imagen': producto.imagen,
                'categoria_id': producto.categoria_id,
                'nombre_categoria': categoria.nombre
            })
        
        return jsonify(productos_data)
        
    except Exception as e:
        print(f"Error en obtener_productos: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500