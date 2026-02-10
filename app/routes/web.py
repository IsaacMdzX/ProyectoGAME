from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from app import db
import datetime
from flask import Flask, request, jsonify
from app.models.pedido import Pedido, PedidoItem
from app.models.usuario import Usuario
from app.models.models import Carrito, CarritoItem, Producto, Categoria
from app.models.role import Role
from app.models.favorito import Favorito
from app.models.analytics import AdminActivity
from sqlalchemy import func

web_bp = Blueprint('web', __name__)

# ----------------------------------------- DECORATORS ---------------------------------------- #

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"🎯 login_required EJECUTÁNDOSE para: {request.path}")
        print(f"🔍 Session data: {dict(session)}")
        print(f"🔍 user_id en session: {'user_id' in session}")
        
        if 'user_id' not in session:
            print("❌ REDIRIGIENDO a login - usuario NO autenticado")
            return redirect(url_for('web.login'))
        
        print("✅ Acceso PERMITIDO - usuario autenticado")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('web.login'))
        
        if session.get('user_role') != 1:  # 1 = Administrador
            return jsonify({'error': 'Acceso denegado. Se requieren privilegios de administrador'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------------------- RUTAS PRINCIPALES ---------------------------------------- #

@web_bp.route('/')
def index():
    return render_template('index.html')

@web_bp.route('/login')
def login():
    return render_template('login.html')

@web_bp.route('/registro')
def registro():
    return render_template('registro.html')

# ----------------------------------------- RUTAS ADMINISTRADOR ---------------------------------------- #

@web_bp.route('/admin/inventario')
@admin_required
def admin_inventario():
    return render_template('admin_templates/inventario.html')

@web_bp.route('/admin/registro')
@admin_required
def admin_registro():
    return render_template('admin_templates/RegistroAdmin.html')

@web_bp.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    return render_template('admin_templates/usuarios.html')


@web_bp.route('/admin/pedidos')
@admin_required
def admin_pedidos():
    return render_template('admin_templates/pedidos.html')

@web_bp.route('/admin/juegos')
@admin_required
def admin_juegos():
    return render_template('admin_templates/juegos.html')

@web_bp.route('/admin/consolas')
@admin_required
def admin_consolas():
    return render_template('admin_templates/consolas.html')

@web_bp.route('/admin/controles')
@admin_required
def admin_controles():
    return render_template('admin_templates/controles.html')

@web_bp.route('/admin/accesorios')
@admin_required
def admin_accesorios():
    return render_template('admin_templates/accesorios.html')

@web_bp.route('/admin/perfil')
@admin_required
def admin_perfil():
    usuario = Usuario.query.get(session['user_id'])
    return render_template('admin_templates/perfil.html', usuario=usuario)

@web_bp.route('/admin')
@admin_required
def admin():
    """Ruta principal del administrador - SOLO accesible para rol 1"""
    return render_template('admin_templates/admin.html')

# ----------------------------------------- RUTAS DE USUARIO ---------------------------------------- #

@web_bp.route('/juegos')
def juegos():
    return render_template('juegos.html')

@web_bp.route('/consolas')
def consolas():
    return render_template('consolas.html')

@web_bp.route('/controles')
def controles():
    return render_template('controles.html')

@web_bp.route('/accesorios')
def accesorios():
    return render_template('accesorios.html')

@web_bp.route('/favoritos')
@login_required
def favoritos():
    return render_template('favoritos.html')

@web_bp.route('/perfil')
@login_required
def perfil():
    usuario = Usuario.query.get(session['user_id'])
    return render_template('perfiluser.html', usuario=usuario)

@web_bp.route('/pedidos')
@login_required
def pedidos():
    return render_template('pedidos.html')

@web_bp.route('/pagar')
@login_required
def pagar():
    return render_template('Pagar.html')

@web_bp.route('/compra-finalizada')
def compra_finalizada():
    return render_template('CompraFinalizada.html')

@web_bp.route('/carrito')
@login_required
def carrito():
    return render_template('Carrito.html')


# ----------------------------------------- AUTENTICACIÓN Y SESIÓN ---------------------------------------- #


@web_bp.route('/pago-exitoso')
def pago_exitoso():
    """Página de confirmación de pago exitoso"""
    return render_template('pago_exitoso.html')

@web_bp.route('/pago-cancelado')
def pago_cancelado():
    """Página cuando el pago es cancelado"""
    return render_template('pago_cancelado.html')


# ----------------------------------------- AUTENTICACIÓN Y SESIÓN ---------------------------------------- #

@web_bp.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos no proporcionados'}), 400
        
        login_input = data.get('login_input')
        password = data.get('password')
        
        if not login_input:
            return jsonify({'error': 'Ingresa tu usuario o email'}), 400
        
        if not password:
            return jsonify({'error': 'Ingresa tu contraseña'}), 400
        
        # Buscar usuario
        usuario = Usuario.query.filter(
            (Usuario.nombre_usuario == login_input) | (Usuario.correo == login_input)
        ).first()
        
        if not usuario:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Verificar contraseña
        if not check_password_hash(usuario.password, password):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Crear sesión
        session.clear()
        session['user_id'] = usuario.id_usuario
        session['username'] = usuario.nombre_usuario
        session['user_role'] = usuario.rol_id
        
        print(f"LOGIN EXITOSO: {usuario.nombre_usuario} (Rol: {usuario.rol_id})")
        
        # Redirigir según rol
        if usuario.rol_id == 1:  # Administrador
            redirect_url = '/admin'
            message = 'Login de administrador exitoso'
        else:  # Usuario normal
            redirect_url = '/'
            message = 'Login exitoso'
        
        return jsonify({
            'success': True, 
            'message': message,
            'redirect_url': redirect_url,
            'user': {
                'id': usuario.id_usuario,
                'username': usuario.nombre_usuario,
                'email': usuario.correo,
                'role': usuario.rol_id
            }
        }), 200
        
    except Exception as e:
        print(f"Error en login: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@web_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@web_bp.route('/api/user-info')
def user_info():
    if 'user_id' in session:
        usuario = Usuario.query.get(session['user_id'])
        return jsonify({
            'logged_in': True,
            'user': {
                'id': usuario.id_usuario,
                'username': usuario.nombre_usuario,
                'email': usuario.correo,
                'role': usuario.rol_id
            }
        })
    else:
        return jsonify({'logged_in': False})

@web_bp.route('/api/usuario/actual')
def api_usuario_actual():
    """Obtener información del usuario actual"""
    try:
        if 'user_id' in session:
            usuario = Usuario.query.get(session['user_id'])
            if not usuario:
                return jsonify({'error': 'Usuario no encontrado'}), 404
            return jsonify({
                'id': usuario.id_usuario,
                'username': usuario.nombre_usuario,
                'email': usuario.correo,
                'role': usuario.rol_id
            })
        else:
            return jsonify({'error': 'No autenticado'}), 401
    except Exception as e:
        print(f"Error en api_usuario_actual: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ----------------------------------------- REGISTROS ---------------------------------------- #

@web_bp.route('/api/registro', methods=['POST'])
def api_registro():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos no proporcionados'}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # Validaciones
        if not username or len(username) < 6:
            return jsonify({'error': 'El nombre de usuario debe tener al menos 6 caracteres'}), 400
        
        if not email or '@' not in email:
            return jsonify({'error': 'Email inválido'}), 400
        
        if not password or len(password) < 8:
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Las contraseñas no coinciden'}), 400
        
        # Verificar si ya existe
        if Usuario.query.filter_by(nombre_usuario=username).first():
            return jsonify({'error': 'Este usuario ya existe'}), 400
            
        if Usuario.query.filter_by(correo=email).first():
            return jsonify({'error': 'Este email ya está registrado'}), 400
        
        # Crear usuario normal
        nuevo_usuario = Usuario(
            nombre_usuario=username,
            correo=email,
            password=generate_password_hash(password),
            rol_id=2  # Cliente
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        print(f"USUARIO GUARDADO EN BD: {username}, Email: {email}")
        
        return jsonify({
            'success': True, 
            'message': 'Usuario registrado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en registro: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@web_bp.route('/api/registro-admin', methods=['POST'])
def api_registro_admin():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos no proporcionados'}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # Validaciones
        if not username or len(username) < 6:
            return jsonify({'error': 'El nombre de usuario debe tener al menos 6 caracteres'}), 400
        
        if not email or '@' not in email:
            return jsonify({'error': 'Email inválido'}), 400
        
        if not password or len(password) < 8:
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Las contraseñas no coinciden'}), 400
        
        # Verificar si ya existe
        if Usuario.query.filter_by(nombre_usuario=username).first():
            return jsonify({'error': 'Este usuario ya existe'}), 400
            
        if Usuario.query.filter_by(correo=email).first():
            return jsonify({'error': 'Este email ya está registrado'}), 400
        
        # Crear administrador
        nuevo_admin = Usuario(
            nombre_usuario=username,
            correo=email,
            password=generate_password_hash(password),
            rol_id=1  # Administrador
        )
        
        db.session.add(nuevo_admin)
        db.session.commit()
        
        print(f"ADMINISTRADOR GUARDADO EN BD: {username}, Email: {email}")
        
        return jsonify({
            'success': True, 
            'message': 'Administrador registrado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en registro admin: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ----------------------------------------- API PRODUCTOS ---------------------------------------- #

@web_bp.route('/api/productos')
def api_productos():
    try:
        # Obtener parámetro de categoría si existe
        categoria_nombre = request.args.get('categoria')
        
        # ✅ SOLO MOSTRAR PRODUCTOS ACTIVOS Y CON STOCK > 0
        if categoria_nombre:
            productos = Producto.query.join(Categoria).filter(
                Categoria.nombre == categoria_nombre,
                Producto.activo == True,
                Producto.stock > 0  # ✅ SOLO productos con stock
            ).all()
            print(f"🔍 Filtrando por categoría: {categoria_nombre}, encontrados: {len(productos)} productos")
        else:
            # Todos los productos activos con stock
            productos = Producto.query.filter(
                Producto.activo == True,
                Producto.stock > 0  # ✅ SOLO productos con stock
            ).all()
            print(f"📦 Todos los productos activos con stock, encontrados: {len(productos)} productos")
        
        productos_data = []
        for producto in productos:
            productos_data.append({
                'id': producto.id_producto,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio': float(producto.precio) if producto.precio else 0,
                'stock': producto.stock,
                'imagen': producto.imagen,
                'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
                'categoria_id': producto.categoria_id
            })
        
        return jsonify({
            'success': True,
            'productos': productos_data,
            'filtro_aplicado': categoria_nombre if categoria_nombre else 'todos'
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo productos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al obtener productos'}), 500

@web_bp.route('/api/productos/categoria/<int:categoria_id>')
def api_productos_por_categoria(categoria_id):
    try:
        # ✅ SOLO productos activos y con stock
        productos = Producto.query.filter(
            Producto.categoria_id == categoria_id,
            Producto.activo == True,
            Producto.stock > 0  # ✅ SOLO productos con stock
        ).all()
        
        productos_data = []
        for producto in productos:
            productos_data.append({
                'id': producto.id_producto,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio': float(producto.precio) if producto.precio else 0,
                'stock': producto.stock,
                'imagen': producto.imagen,
                'categoria_id': producto.categoria_id
            })
        
        return jsonify({
            'success': True,
            'productos': productos_data
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo productos por categoría: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener productos'}), 500

# ----------------------------------------- CARRITO API ---------------------------------------- #

@web_bp.route('/api/carrito/cantidad')
def api_carrito_cantidad():
    """Obtener cantidad de items en el carrito"""
    try:
        if 'user_id' not in session:
            return jsonify({'count': 0})
        
        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()
        
        count = len(carrito.items) if carrito else 0
        return jsonify({'count': count})
        
    except Exception as e:
        print(f"Error obteniendo cantidad del carrito: {e}")
        return jsonify({'count': 0})

@web_bp.route('/api/carrito/agregar', methods=['POST'])
def agregar_al_carrito():
    try:
        print(f"🎯 INICIANDO agregar_al_carrito - User: {session.get('user_id')}")
        
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Inicia sesion para poder agregar productos al carrito'}), 401

        data = request.get_json()
        print(f"📦 Datos recibidos: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'Datos no proporcionados'}), 400

        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad', 1)

        if not producto_id:
            return jsonify({'success': False, 'error': 'ID de producto no proporcionado'}), 400

        # Convertir a entero para evitar problemas de tipo
        producto_id = int(producto_id)
        cantidad = int(cantidad)

        print(f"🔍 Buscando producto {producto_id}")
        producto = Producto.query.filter_by(id_producto=producto_id, activo=True).first()
        
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # Buscar carrito activo del usuario
        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()

        print(f"🛒 Carrito encontrado: {carrito.id_carrito if carrito else 'NONE'}")

        if not carrito:
            carrito = Carrito(usuario_id=session['user_id'])
            db.session.add(carrito)
            db.session.flush()
            print(f"🆕 Nuevo carrito creado: {carrito.id_carrito}")

        # ✅ VERIFICACIÓN MÁS ROBUSTA: Buscar item existente
        item_existente = CarritoItem.query.filter_by(
            carrito_id=carrito.id_carrito,
            producto_id=producto_id
        ).first()

        print(f"🔍 Item existente: {item_existente.id_item if item_existente else 'NONE'}")

        if item_existente:
            # Si ya existe, aumentar la cantidad
            nueva_cantidad = item_existente.cantidad + cantidad
            print(f"📈 Actualizando cantidad: {item_existente.cantidad} + {cantidad} = {nueva_cantidad}")
            
            # Verificar stock disponible
            if nueva_cantidad > producto.stock:
                return jsonify({'success': False, 'error': f'Stock insuficiente. Solo quedan {producto.stock} unidades'}), 400
            
            item_existente.cantidad = nueva_cantidad
            mensaje = f'Cantidad actualizada: ahora tienes {nueva_cantidad} unidades'
            accion = 'actualizado'
        else:
            # Si no existe, crear nuevo item
            print(f"🆕 Creando nuevo item para producto {producto_id}")
            nuevo_item = CarritoItem(
                carrito_id=carrito.id_carrito,
                producto_id=producto_id,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            db.session.add(nuevo_item)
            mensaje = 'Producto agregado al carrito'
            accion = 'agregado'

        db.session.commit()
        print(f"✅ Commit exitoso - {accion}")
        
        # Obtener el conteo actualizado
        carrito_actualizado = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()
        
        count = len(carrito_actualizado.items) if carrito_actualizado else 0
        
        print(f"🎉 Carrito {accion} exitosamente. Total items: {count}")
        
        return jsonify({
            'success': True, 
            'message': mensaje,
            'carrito_count': count,
            'accion': accion
        })

    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR en agregar_al_carrito: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@web_bp.route('/api/carrito/detalles')
def api_carrito_detalles():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401

        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()

        if not carrito:
            return jsonify({
                'success': True,
                'carrito': {
                    'items': [],
                    'subtotal': 0,
                    'total': 0,
                    'count': 0
                }
            })

        items_data = []
        subtotal = 0
        
        for item in carrito.items:
            item_total = float(item.precio_unitario) * item.cantidad
            subtotal += item_total
            
            items_data.append({
                'id': item.id_item,
                'producto_id': item.producto.id_producto,
                'nombre': item.producto.nombre,
                'precio_unitario': float(item.precio_unitario),
                'cantidad': item.cantidad,
                'total': item_total,
                'imagen': item.producto.imagen,
                'stock': item.producto.stock
            })

        return jsonify({
            'success': True,
            'carrito': {
                'items': items_data,
                'subtotal': subtotal,
                'total': subtotal,
                'count': len(carrito.items)
            }
        })

    except Exception as e:
        print(f"Error obteniendo carrito: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

@web_bp.route('/api/carrito/actualizar/<int:item_id>', methods=['PUT'])
def actualizar_cantidad_carrito(item_id):
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401

        data = request.get_json()
        nueva_cantidad = data.get('cantidad', 1)

        item = CarritoItem.query.get(item_id)
        
        if not item:
            return jsonify({'success': False, 'error': 'Item no encontrado'}), 404

        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()
        
        if not carrito or item.carrito_id != carrito.id_carrito:
            return jsonify({'success': False, 'error': 'No autorizado'}), 403

        producto = Producto.query.get(item.producto_id)
        if nueva_cantidad > producto.stock:
            return jsonify({'success': False, 'error': 'Stock insuficiente'}), 400

        if nueva_cantidad <= 0:
            db.session.delete(item)
        else:
            item.cantidad = nueva_cantidad

        db.session.commit()
        return jsonify({'success': True, 'message': 'Carrito actualizado'})

    except Exception as e:
        db.session.rollback()
        print(f"Error actualizando carrito: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

@web_bp.route('/api/carrito/eliminar/<int:item_id>', methods=['DELETE'])
def eliminar_item_carrito(item_id):
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401

        item = CarritoItem.query.get(item_id)
        
        if not item:
            return jsonify({'success': False, 'error': 'Item no encontrado'}), 404

        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()
        
        if not carrito or item.carrito_id != carrito.id_carrito:
            return jsonify({'success': False, 'error': 'No autorizado'}), 403

        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Producto eliminado del carrito'})

    except Exception as e:
        db.session.rollback()
        print(f"Error eliminando item: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

@web_bp.route('/api/carrito/limpiar-duplicados', methods=['POST'])
@login_required
def limpiar_duplicados_carrito():
    """Limpiar productos duplicados del carrito"""
    try:
        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()

        if not carrito:
            return jsonify({'success': True, 'message': 'No hay carrito'})

        # Encontrar duplicados
        items_por_producto = {}
        items_a_eliminar = []
        
        for item in carrito.items:
            if item.producto_id in items_por_producto:
                # Ya existe un item para este producto, marcar para eliminar
                items_a_eliminar.append(item)
                # Sumar la cantidad al item existente
                items_por_producto[item.producto_id].cantidad += item.cantidad
            else:
                items_por_producto[item.producto_id] = item

        # Eliminar duplicados
        for item in items_a_eliminar:
            db.session.delete(item)

        if items_a_eliminar:
            db.session.commit()
            return jsonify({
                'success': True, 
                'message': f'Se limpiaron {len(items_a_eliminar)} productos duplicados',
                'duplicados_eliminados': len(items_a_eliminar)
            })
        else:
            return jsonify({'success': True, 'message': 'No se encontraron duplicados'})

    except Exception as e:
        db.session.rollback()
        print(f"Error limpiando duplicados: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

# ----------------------------------------- API FAVORITOS ---------------------------------------- #

@web_bp.route('/api/favoritos')
@login_required
def api_favoritos():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Debes iniciar sesión para ver favoritos'}), 401
        
        usuario_id = session['user_id']
        
        # Obtener favoritos con información del producto y categoría
        favoritos = Favorito.query.filter_by(usuario_id=usuario_id)\
            .join(Producto)\
            .join(Categoria)\
            .all()
        
        favoritos_data = []
        for favorito in favoritos:
            producto = favorito.producto
            favoritos_data.append({
                'id': favorito.id_favorito,
                'fecha_agregado': favorito.fecha_agregado.isoformat() if favorito.fecha_agregado else None,
                'producto': {
                    'id': producto.id_producto,
                    'nombre': producto.nombre,
                    'descripcion': producto.descripcion,
                    'precio': float(producto.precio) if producto.precio else 0,
                    'stock': producto.stock,
                    'imagen': producto.imagen,
                    'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
                    'categoria_id': producto.categoria_id
                }
            })
        
        return jsonify({
            'success': True,
            'favoritos': favoritos_data,
            'count': len(favoritos)
        })
        
    except Exception as e:
        print(f"Error obteniendo favoritos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al obtener favoritos'}), 500

@web_bp.route('/api/favoritos/agregar', methods=['POST'])
@login_required
def api_agregar_favorito():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Datos no proporcionados'}), 400

        producto_id = data.get('producto_id')
        if not producto_id:
            return jsonify({'success': False, 'error': 'ID de producto no proporcionado'}), 400

        # Verificar si el producto existe
        producto = Producto.query.filter_by(id_producto=producto_id, activo=True).first()
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # Verificar si ya está en favoritos
        favorito_existente = Favorito.query.filter_by(
            usuario_id=session['user_id'],
            producto_id=producto_id
        ).first()

        if favorito_existente:
            return jsonify({'success': False, 'error': 'El producto ya está en favoritos'}), 400

        # Agregar a favoritos
        nuevo_favorito = Favorito(
            usuario_id=session['user_id'],
            producto_id=producto_id
        )

        db.session.add(nuevo_favorito)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Producto agregado a favoritos'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error agregando favorito: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@web_bp.route('/api/favoritos/eliminar/<int:producto_id>', methods=['DELETE'])
@login_required
def api_eliminar_favorito(producto_id):
    try:
        favorito = Favorito.query.filter_by(
            usuario_id=session['user_id'],
            producto_id=producto_id
        ).first()

        if not favorito:
            return jsonify({'success': False, 'error': 'Favorito no encontrado'}), 404

        db.session.delete(favorito)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Producto eliminado de favoritos'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error eliminando favorito: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@web_bp.route('/api/favoritos/verificar/<int:producto_id>')
@login_required
def api_verificar_favorito(producto_id):
    try:
        favorito = Favorito.query.filter_by(
            usuario_id=session['user_id'],
            producto_id=producto_id
        ).first()

        return jsonify({
            'success': True,
            'es_favorito': favorito is not None
        })

    except Exception as e:
        print(f"Error verificando favorito: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

# ----------------------------------------- API ADMIN PRODUCTOS ---------------------------------------- #

@web_bp.route('/api/admin/productos')
@admin_required
def api_admin_productos():
    try:
        # Obtener parámetros de filtro
        search = request.args.get('search', '')
        categoria_id = request.args.get('categoria', '')
        estado = request.args.get('estado', '')

        # Consulta base
        query = Producto.query.join(Categoria)

        # Aplicar filtros
        if search:
            query = query.filter(Producto.nombre.ilike(f'%{search}%'))
        
        if categoria_id:
            query = query.filter(Producto.categoria_id == categoria_id)
        
        if estado:
            if estado == 'activo':
                query = query.filter(Producto.activo == True)
            elif estado == 'inactivo':
                query = query.filter(Producto.activo == False)

        productos = query.order_by(Producto.fecha_creacion.desc()).all()

        productos_data = []
        for producto in productos:
            productos_data.append({
                'id': producto.id_producto,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio': float(producto.precio) if producto.precio else 0,
                'stock': producto.stock,
                'imagen': producto.imagen,
                'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
                'categoria_id': producto.categoria_id,
                'activo': producto.activo,
                'fecha_creacion': producto.fecha_creacion.isoformat() if producto.fecha_creacion else None
            })

        return jsonify({
            'success': True,
            'productos': productos_data
        })
        
    except Exception as e:
        print(f"Error obteniendo productos admin: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener productos'}), 500

@web_bp.route('/api/categorias')
@admin_required
def api_categorias():
    try:
        categorias = Categoria.query.all()
        
        categorias_data = [{
            'id': cat.id_categoria,
            'nombre': cat.nombre,
            'descripcion': cat.descripcion
        } for cat in categorias]

        return jsonify({
            'success': True,
            'categorias': categorias_data
        })
        
    except Exception as e:
        print(f"Error obteniendo categorías: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener categorías'}), 500

@web_bp.route('/api/admin/productos/agregar', methods=['POST'])
@admin_required
def api_admin_agregar_producto():
    try:
        data = request.get_json()
        
        # Validaciones básicas
        if not data.get('nombre'):
            return jsonify({'success': False, 'error': 'El nombre es requerido'}), 400
        
        if not data.get('precio') or float(data.get('precio')) <= 0:
            return jsonify({'success': False, 'error': 'El precio debe ser mayor a 0'}), 400
        
        if data.get('stock') is None or int(data.get('stock')) < 0:
            return jsonify({'success': False, 'error': 'El stock no puede ser negativo'}), 400

        if not data.get('categoria_id'):
            return jsonify({'success': False, 'error': 'La categoría es requerida'}), 400

        # Crear nuevo producto
        nuevo_producto = Producto(
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion', ''),
            precio=float(data.get('precio')),
            stock=int(data.get('stock')),
            imagen=data.get('imagen', ''),
            categoria_id=data.get('categoria_id'),
            activo=data.get('activo', True)
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Producto agregado correctamente',
            'producto_id': nuevo_producto.id_producto
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error agregando producto: {e}")
        return jsonify({'success': False, 'error': 'Error al agregar producto'}), 500

@web_bp.route('/api/admin/productos/editar', methods=['PUT'])
@admin_required
def api_admin_editar_producto():
    try:
        data = request.get_json()
        producto_id = data.get('id')
        
        if not producto_id:
            return jsonify({'success': False, 'error': 'ID de producto requerido'}), 400

        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # Actualizar campos
        stock_anterior = producto.stock
        if 'nombre' in data:
            producto.nombre = data['nombre']
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        if 'precio' in data:
            producto.precio = float(data['precio'])
        if 'stock' in data:
            nuevo_stock = int(data['stock'])
            producto.stock = nuevo_stock
            
            # ✅ DESHABILITAR SI EL NUEVO STOCK ES 0
            if nuevo_stock == 0:
                producto.activo = False
            # ✅ HABILITAR SI HABÍA STOCK 0 Y AHORA TIENE STOCK
            elif nuevo_stock > 0 and stock_anterior == 0:
                producto.activo = True
                
        if 'imagen' in data:
            producto.imagen = data['imagen']
        if 'categoria_id' in data:
            producto.categoria_id = data['categoria_id']
        if 'activo' in data:
            # Si el admin manualmente activa un producto con stock 0, prevenir
            if data['activo'] and producto.stock == 0:
                return jsonify({
                    'success': False, 
                    'error': 'No se puede activar un producto con stock 0'
                }), 400
            producto.activo = data['activo']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Producto actualizado correctamente'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error editando producto: {e}")
        return jsonify({'success': False, 'error': 'Error al editar producto'}), 500

@web_bp.route('/api/admin/productos/estado', methods=['PUT'])
@admin_required
def api_admin_cambiar_estado():
    try:
        data = request.get_json()
        producto_id = data.get('id')
        activo = data.get('activo')

        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # Cambiar estado sin restricciones
        producto.activo = activo
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Estado del producto actualizado correctamente'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error cambiando estado: {e}")
        return jsonify({'success': False, 'error': 'Error al cambiar estado'}), 500

@web_bp.route('/api/admin/productos/eliminar/<int:producto_id>', methods=['DELETE'])
@admin_required
def api_admin_eliminar_producto(producto_id):
    try:
        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # 1. Eliminar items del carrito relacionados
        items_carrito = CarritoItem.query.filter_by(producto_id=producto_id).all()
        for item in items_carrito:
            db.session.delete(item)

        # 2. Eliminar favoritos relacionados
        from app.models.favorito import Favorito
        favoritos = Favorito.query.filter_by(producto_id=producto_id).all()
        for favorito in favoritos:
            db.session.delete(favorito)

        # 3. Finalmente eliminar el producto
        db.session.delete(producto)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Producto eliminado correctamente'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error eliminando producto: {e}")
        return jsonify({'success': False, 'error': 'Error al eliminar producto'}), 500

# ----------------------------------------- API PEDIDOS ---------------------------------------- #

@web_bp.route('/api/pedidos/procesar', methods=['POST'])
@login_required
def api_procesar_pedido():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401

        data = request.get_json()
        metodo_pago = data.get('metodo_pago', 'paypal')
        detalles_paypal = data.get('detalles_paypal', {})
        detalles_mercadopago = data.get('detalles_mercadopago', {})
        
        print(f"🎯 Procesando pedido para usuario {session['user_id']}")

        # Obtener el carrito activo del usuario
        carrito = Carrito.query.filter_by(
            usuario_id=session['user_id'], 
            activo=True
        ).first()

        if not carrito or not carrito.items:
            return jsonify({'success': False, 'error': 'Carrito vacío'}), 400

        # Verificar stock y calcular total
        total_pedido = 0
        items_pedido = []
        
        for item in carrito.items:
            producto = Producto.query.get(item.producto_id)
            
            if not producto or not producto.activo:
                return jsonify({
                    'success': False, 
                    'error': f'El producto {producto.nombre if producto else "desconocido"} no está disponible'
                }), 400
            
            if producto.stock < item.cantidad:
                return jsonify({
                    'success': False, 
                    'error': f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}, Solicitado: {item.cantidad}'
                }), 400
            
            # Calcular total del item
            item_total = float(item.precio_unitario) * item.cantidad
            total_pedido += item_total
            items_pedido.append({
                'producto': producto,
                'item_carrito': item,
                'cantidad': item.cantidad,
                'precio': float(item.precio_unitario),
                'total': item_total
            })

        # ✅ CREAR PEDIO CON INFORMACIÓN DE PAYPAL
        nuevo_pedido = Pedido(
            usuario_id=session['user_id'],
            total=total_pedido,
            estado='completado',  # Cambiar a 'pendiente' si quieres confirmación manual
            metodo_pago=metodo_pago,
            id_transaccion_paypal=detalles_paypal.get('id', ''),  # Guardar ID de transacción PayPal
            id_transaccion_mercadopago=detalles_mercadopago.get('id', '')  # Guardar ID de transacción Mercado Pago
        )
        
        db.session.add(nuevo_pedido)
        db.session.flush()  # Para obtener el ID del pedido

        # Crear items del pedido y actualizar stock
        for item_data in items_pedido:
            producto = item_data['producto']
            item_carrito = item_data['item_carrito']
            
            # Crear item del pedido
            pedido_item = PedidoItem(
                pedido_id=nuevo_pedido.id_pedido,
                producto_id=producto.id_producto,
                cantidad=item_carrito.cantidad,
                precio_unitario=item_carrito.precio_unitario
            )
            db.session.add(pedido_item)
            
            # Actualizar stock del producto
            producto.stock -= item_carrito.cantidad
            
            # Deshabilitar producto si stock llega a 0
            if producto.stock == 0:
                producto.activo = False
                print(f"⚠️ Producto deshabilitado por stock 0: {producto.nombre}")

        # Limpiar el carrito
        for item in carrito.items:
            db.session.delete(item)
        
        carrito.activo = False

        db.session.commit()

        print(f"✅ Pedido {nuevo_pedido.id_pedido} procesado exitosamente. Total: ${total_pedido}")

        # Seleccionar el id de transacción según el método de pago
        transaccion_id = nuevo_pedido.id_transaccion_paypal
        if metodo_pago == 'mercadopago':
            transaccion_id = nuevo_pedido.id_transaccion_mercadopago

        return jsonify({
            'success': True,
            'message': 'Compra procesada correctamente',
            'pedido_id': nuevo_pedido.id_pedido,
            'total': float(total_pedido),
            'transaccion_id': transaccion_id
        })

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error procesando pedido: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al procesar la compra'}), 500


@web_bp.route('/api/pedidos/crear-mercadopago', methods=['POST'])
@login_required
def api_crear_pedido_mercadopago():
    """Crear un pedido en estado 'pendiente' para ser asociado a una preference de Mercado Pago.

    No reduce stock ni limpia el carrito; eso se hace cuando la transacción sea confirmada por el webhook.
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401

        # Obtener el carrito activo del usuario
        carrito = Carrito.query.filter_by(usuario_id=session['user_id'], activo=True).first()
        if not carrito or not carrito.items:
            return jsonify({'success': False, 'error': 'Carrito vacío'}), 400

        # Calcular total y crear pedido en estado pendiente
        total_pedido = 0
        for item in carrito.items:
            total_pedido += float(item.precio_unitario) * item.cantidad

        nuevo_pedido = Pedido(
            usuario_id=session['user_id'],
            total=total_pedido,
            estado='pendiente',
            metodo_pago='mercadopago'
        )
        db.session.add(nuevo_pedido)
        db.session.flush()

        # Crear items del pedido (no tocar stock)
        for item in carrito.items:
            pedido_item = PedidoItem(
                pedido_id=nuevo_pedido.id_pedido,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario
            )
            db.session.add(pedido_item)

        db.session.commit()

        return jsonify({'success': True, 'pedido_id': nuevo_pedido.id_pedido})

    except Exception as e:
        db.session.rollback()
        print(f"Error creando pedido Mercado Pago: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error creando pedido'}), 500

# ----------------------------------------- API USUARIOS ADMIN ---------------------------------------- #

@web_bp.route('/api/admin/usuarios')
@admin_required
def api_admin_usuarios():
    """Obtener todos los usuarios para administración"""
    try:
        # Obtener parámetros de filtro
        search = request.args.get('search', '')
        rol_id = request.args.get('rol', '')
        estado = request.args.get('estado', '')

        # Consulta base
        query = Usuario.query.join(Role)

        # Aplicar filtros
        if search:
            query = query.filter(
                (Usuario.nombre_usuario.ilike(f'%{search}%')) |
                (Usuario.correo.ilike(f'%{search}%'))
            )
        
        if rol_id:
            query = query.filter(Usuario.rol_id == rol_id)
        
        if estado:
            if estado == 'activo':
                query = query.filter(Usuario.activo == True)
            elif estado == 'inactivo':
                query = query.filter(Usuario.activo == False)

        usuarios = query.order_by(Usuario.fecha_registro.desc()).all()

        usuarios_data = []
        for usuario in usuarios:
            usuarios_data.append({
                'id': usuario.id_usuario,
                'username': usuario.nombre_usuario,
                'email': usuario.correo,
                'rol': usuario.rol.nombre if usuario.rol else 'Sin rol',
                'rol_id': usuario.rol_id,
                'activo': usuario.activo,
                'fecha_registro': usuario.fecha_registro.isoformat() if usuario.fecha_registro else None,
                'ultimo_login': usuario.ultimo_acceso.isoformat() if usuario.ultimo_acceso else None
            })

        return jsonify({
            'success': True,
            'usuarios': usuarios_data,
            'total': len(usuarios_data)
        })
        
    except Exception as e:
        print(f"Error obteniendo usuarios admin: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al obtener usuarios'}), 500

@web_bp.route('/api/admin/usuarios/editar', methods=['PUT'])
@admin_required
def api_admin_editar_usuario():
    """Editar usuario desde administración"""
    try:
        data = request.get_json()
        usuario_id = data.get('id')
        
        if not usuario_id:
            return jsonify({'success': False, 'error': 'ID de usuario requerido'}), 400

        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

        # Verificar que no se modifique a sí mismo
        if usuario.id_usuario == session['user_id']:
            return jsonify({'success': False, 'error': 'No puedes modificar tu propio usuario desde aquí'}), 400

        # Actualizar campos
        if 'username' in data:
            # Verificar si el username ya existe (excluyendo el usuario actual)
            existing_user = Usuario.query.filter(
                Usuario.nombre_usuario == data['username'],
                Usuario.id_usuario != usuario_id
            ).first()
            if existing_user:
                return jsonify({'success': False, 'error': 'Este nombre de usuario ya está en uso'}), 400
            usuario.nombre_usuario = data['username']

        if 'email' in data:
            # Verificar si el email ya existe (excluyendo el usuario actual)
            existing_email = Usuario.query.filter(
                Usuario.correo == data['email'],
                Usuario.id_usuario != usuario_id
            ).first()
            if existing_email:
                return jsonify({'success': False, 'error': 'Este email ya está en uso'}), 400
            usuario.correo = data['email']

        if 'rol_id' in data:
            usuario.rol_id = data['rol_id']

        if 'activo' in data:
            usuario.activo = data['activo']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Usuario actualizado correctamente'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error editando usuario: {e}")
        return jsonify({'success': False, 'error': 'Error al editar usuario'}), 500

@web_bp.route('/api/admin/usuarios/agregar', methods=['POST'])
@admin_required
def api_admin_agregar_usuario():
    """Agregar nuevo usuario desde administración"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Datos no proporcionados'}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        rol_id = data.get('rol_id', 2)  # Por defecto cliente
        activo = data.get('activo', True)

        # Validaciones
        if not username or len(username) < 6:
            return jsonify({'success': False, 'error': 'El nombre de usuario debe tener al menos 6 caracteres'}), 400
        
        if not email or '@' not in email:
            return jsonify({'success': False, 'error': 'Email inválido'}), 400
        
        if not password or len(password) < 8:
            return jsonify({'success': False, 'error': 'La contraseña debe tener al menos 8 caracteres'}), 400

        # Verificar si ya existe
        if Usuario.query.filter_by(nombre_usuario=username).first():
            return jsonify({'success': False, 'error': 'Este usuario ya existe'}), 400
            
        if Usuario.query.filter_by(correo=email).first():
            return jsonify({'success': False, 'error': 'Este email ya está registrado'}), 400

        # Crear usuario
        nuevo_usuario = Usuario(
            nombre_usuario=username,
            correo=email,
            password=generate_password_hash(password),
            rol_id=rol_id,
            activo=activo
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        print(f"USUARIO ADMIN CREADO: {username}, Email: {email}, Rol: {rol_id}")
        
        return jsonify({
            'success': True, 
            'message': 'Usuario creado exitosamente',
            'usuario_id': nuevo_usuario.id_usuario
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creando usuario admin: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@web_bp.route('/api/admin/usuarios/eliminar/<int:usuario_id>', methods=['DELETE'])
@admin_required
def api_admin_eliminar_usuario(usuario_id):
    """Eliminar usuario desde administración"""
    try:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

        # Verificar que no se elimine a sí mismo
        if usuario.id_usuario == session['user_id']:
            return jsonify({'success': False, 'error': 'No puedes eliminar tu propio usuario'}), 400

        db.session.delete(usuario)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Usuario eliminado correctamente'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error eliminando usuario: {e}")
        return jsonify({'success': False, 'error': 'Error al eliminar usuario'}), 500

@web_bp.route('/api/admin/roles')
@admin_required
def api_admin_roles():
    """Obtener todos los roles"""
    try:
        roles = Role.query.all()
        
        roles_data = [{
            'id_rol': rol.id_rol,
            'nombre': rol.nombre,
        } for rol in roles]

        return jsonify({
            'success': True,
            'roles': roles_data
        })
        
    except Exception as e:
        print(f"Error obteniendo roles: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al obtener roles'}), 500

# ----------------------------------------- API PEDIDOS ADMIN ---------------------------------------- #

@web_bp.route('/api/admin/pedidos')
@admin_required
def api_admin_pedidos():
    """Obtener todos los pedidos para administración"""
    try:
        from app.models.pedido import Pedido, PedidoItem
        from app.models.usuario import Usuario
        from app.models.models import Producto
        
        # Obtener parámetros de filtro
        search = request.args.get('search', '')
        estado = request.args.get('estado', '')
        fecha_inicio = request.args.get('fecha_inicio', '')
        fecha_fin = request.args.get('fecha_fin', '')
        
        # Consulta base con joins
        query = Pedido.query.join(Usuario).join(PedidoItem).join(Producto)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                (Usuario.nombre_usuario.ilike(f'%{search}%')) |
                (Usuario.correo.ilike(f'%{search}%')) |
                (Producto.nombre.ilike(f'%{search}%')) |
                (Pedido.id_pedido.ilike(f'%{search}%'))
            )
        
        if estado:
            query = query.filter(Pedido.estado == estado)
        
        if fecha_inicio:
            query = query.filter(Pedido.fecha_pedido >= fecha_inicio)
        
        if fecha_fin:
            query = query.filter(Pedido.fecha_pedido <= fecha_fin)
        
        # Ordenar por fecha más reciente primero
        pedidos = query.order_by(Pedido.fecha_pedido.desc()).all()
        
        # Procesar datos para el frontend
        pedidos_data = []
        for pedido in pedidos:
            # Obtener todos los items del pedido
            items_data = []
            for item in pedido.items:
                items_data.append({
                    'producto_nombre': item.producto.nombre if item.producto else 'Producto no disponible',
                    'cantidad': item.cantidad,
                    'precio_unitario': float(item.precio_unitario) if item.precio_unitario else 0,
                    'total_item': float(item.precio_unitario * item.cantidad) if item.precio_unitario else 0
                })
            
            pedidos_data.append({
                'id_pedido': pedido.id_pedido,
                'numero_pedido': f"#ORD-{pedido.id_pedido:03d}",
                'cliente_nombre': pedido.usuario.nombre_usuario if pedido.usuario else 'Cliente no disponible',
                'cliente_email': pedido.usuario.correo if pedido.usuario else '',
                'productos': items_data,
                'cantidad_total': sum(item.cantidad for item in pedido.items),
                'total_pedido': float(pedido.total) if pedido.total else 0,
                'estado': pedido.estado,
                'fecha_pedido': pedido.fecha_pedido.strftime('%Y-%m-%d %H:%M') if pedido.fecha_pedido else '',
                'fecha_iso': pedido.fecha_pedido.isoformat() if pedido.fecha_pedido else '',
                'direccion_envio': pedido.direccion_envio or 'No especificada'
            })
        
        return jsonify({
            'success': True,
            'pedidos': pedidos_data,
            'total': len(pedidos_data),
            'filtros_aplicados': {
                'search': search,
                'estado': estado,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }
        })
        
    except Exception as e:
        print(f"Error obteniendo pedidos admin: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al obtener pedidos'}), 500

@web_bp.route('/api/admin/pedidos/estado', methods=['PUT'])
@admin_required
def api_admin_cambiar_estado_pedido():
    """Cambiar estado de un pedido"""
    try:
        from app.models.pedido import Pedido
        
        data = request.get_json()
        pedido_id = data.get('pedido_id')
        nuevo_estado = data.get('estado')
        
        if not pedido_id or not nuevo_estado:
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        # Validar estado
        estados_validos = ['pendiente', 'procesando', 'completado', 'cancelado']
        if nuevo_estado not in estados_validos:
            return jsonify({'success': False, 'error': 'Estado no válido'}), 400
        
        pedido.estado = nuevo_estado
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Estado del pedido actualizado a {nuevo_estado}',
            'nuevo_estado': nuevo_estado
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error cambiando estado de pedido: {e}")
        return jsonify({'success': False, 'error': 'Error al cambiar estado'}), 500

@web_bp.route('/api/admin/pedidos/<int:pedido_id>')
@admin_required
def api_admin_detalle_pedido(pedido_id):
    """Obtener detalle completo de un pedido"""
    try:
        from app.models.pedido import Pedido, PedidoItem
        from app.models.usuario import Usuario
        from app.models.models import Producto
        
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        # Datos del pedido
        pedido_data = {
            'id_pedido': pedido.id_pedido,
            'numero_pedido': f"#ORD-{pedido.id_pedido:03d}",
            'cliente': {
                'id': pedido.usuario.id_usuario,
                'nombre': pedido.usuario.nombre_usuario,
                'email': pedido.usuario.correo,
                'telefono': pedido.usuario.telefono
            } if pedido.usuario else None,
            'fecha_pedido': pedido.fecha_pedido.strftime('%Y-%m-%d %H:%M') if pedido.fecha_pedido else '',
            'total': float(pedido.total) if pedido.total else 0,
            'estado': pedido.estado,
            'direccion_envio': pedido.direccion_envio
        }
        
        # Items del pedido
        items_data = []
        for item in pedido.items:
            items_data.append({
                'producto_id': item.producto_id,
                'producto_nombre': item.producto.nombre if item.producto else 'Producto no disponible',
                'cantidad': item.cantidad,
                'precio_unitario': float(item.precio_unitario) if item.precio_unitario else 0,
                'total': float(item.precio_unitario * item.cantidad) if item.precio_unitario else 0,
                'imagen': item.producto.imagen if item.producto else ''
            })
        
        pedido_data['items'] = items_data
        
        return jsonify({
            'success': True,
            'pedido': pedido_data
        })
        
    except Exception as e:
        print(f"Error obteniendo detalle de pedido: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener detalle'}), 500

# ----------------------------------------- DASHBOARD ADMIN ---------------------------------------- #

@web_bp.route('/api/admin/dashboard/summary')
@admin_required
def api_admin_dashboard_summary():
    try:
        today = datetime.date.today()
        daily_sales = db.session.query(func.coalesce(func.sum(Pedido.total), 0)).filter(
            func.date(Pedido.fecha_pedido) == today,
            Pedido.estado != 'cancelado'
        ).scalar()

        pending_orders = Pedido.query.filter(Pedido.estado.in_(['pendiente', 'procesando'])).count()
        low_stock = Producto.query.filter(Producto.stock < 10, Producto.activo == True).count()
        active_customers = Usuario.query.filter(Usuario.activo == True, Usuario.rol_id == 2).count()

        return jsonify({
            'success': True,
            'summary': {
                'daily_sales': float(daily_sales or 0),
                'pending_orders': pending_orders,
                'low_stock': low_stock,
                'active_customers': active_customers
            }
        })
    except Exception as e:
        print(f"Error dashboard summary: {e}")
        return jsonify({'success': False, 'error': 'Error al cargar resumen'}), 500


@web_bp.route('/api/admin/dashboard/sales')
@admin_required
def api_admin_dashboard_sales():
    try:
        period = request.args.get('period', 'month')
        today = datetime.date.today()

        if period == 'week':
            start_date = today - datetime.timedelta(days=6)
            group_format = '%Y-%m-%d'
            label_format = '%d %b'
            truncate = func.date(Pedido.fecha_pedido)
        elif period == 'year':
            start_date = today - datetime.timedelta(days=365)
            group_format = '%Y-%m'
            label_format = '%b %Y'
            truncate = func.date_trunc('month', Pedido.fecha_pedido)
        else:
            start_date = today - datetime.timedelta(days=29)
            group_format = '%Y-%m-%d'
            label_format = '%d %b'
            truncate = func.date(Pedido.fecha_pedido)

        rows = db.session.query(
            truncate.label('period'),
            func.coalesce(func.sum(Pedido.total), 0)
        ).filter(
            Pedido.estado != 'cancelado',
            Pedido.fecha_pedido >= start_date
        ).group_by('period').order_by('period').all()

        data_map = {}
        for row in rows:
            period_key = row[0]
            if hasattr(period_key, 'date'):
                period_key = period_key.date()
            if period == 'year':
                key = period_key.strftime('%Y-%m') if hasattr(period_key, 'strftime') else str(period_key)
            else:
                key = period_key.strftime('%Y-%m-%d') if hasattr(period_key, 'strftime') else str(period_key)
            data_map[key] = float(row[1] or 0)

        labels = []
        data = []

        if period == 'year':
            current = datetime.date(today.year, today.month, 1)
            for _ in range(12):
                key = current.strftime(group_format)
                labels.append(current.strftime(label_format))
                data.append(data_map.get(key, 0))
                month = current.month - 1
                year = current.year
                if month == 0:
                    month = 12
                    year -= 1
                current = datetime.date(year, month, 1)
            labels.reverse()
            data.reverse()
        else:
            current = start_date
            while current <= today:
                key = current.strftime(group_format)
                labels.append(current.strftime(label_format))
                data.append(data_map.get(key, 0))
                current += datetime.timedelta(days=1)

        return jsonify({
            'success': True,
            'chart': {
                'labels': labels,
                'data': data
            }
        })
    except Exception as e:
        print(f"Error dashboard sales: {e}")
        return jsonify({'success': False, 'error': 'Error al cargar ventas'}), 500


@web_bp.route('/api/admin/dashboard/top-products')
@admin_required
def api_admin_dashboard_top_products():
    try:
        rows = db.session.query(
            Producto.nombre,
            func.coalesce(func.sum(PedidoItem.cantidad), 0).label('total')
        ).join(PedidoItem, PedidoItem.producto_id == Producto.id_producto)
        rows = rows.group_by(Producto.nombre).order_by(func.sum(PedidoItem.cantidad).desc()).limit(5).all()

        labels = [row[0] for row in rows]
        data = [int(row[1]) for row in rows]

        return jsonify({
            'success': True,
            'chart': {
                'labels': labels,
                'data': data
            }
        })
    except Exception as e:
        print(f"Error dashboard top products: {e}")
        return jsonify({'success': False, 'error': 'Error al cargar top productos'}), 500


@web_bp.route('/api/admin/dashboard/recent-activity')
@admin_required
def api_admin_dashboard_recent_activity():
    try:
        activity = []

        recent_logs = AdminActivity.query.order_by(AdminActivity.creado_en.desc()).limit(6).all()
        if recent_logs:
            for log in recent_logs:
                activity.append({
                    'title': log.tipo.title(),
                    'description': log.descripcion,
                    'timestamp': log.creado_en.isoformat(),
                    'icon': '✓',
                    'icon_class': 'success'
                })
        else:
            recent_orders = Pedido.query.order_by(Pedido.fecha_pedido.desc()).limit(3).all()
            for pedido in recent_orders:
                activity.append({
                    'title': 'Pedido reciente',
                    'description': f"Orden #ORD-{pedido.id_pedido:03d} - ${float(pedido.total or 0):.2f}",
                    'timestamp': pedido.fecha_pedido.isoformat() if pedido.fecha_pedido else None,
                    'icon': '📦',
                    'icon_class': 'info'
                })

            low_stock = Producto.query.filter(Producto.stock < 10).order_by(Producto.stock.asc()).limit(2).all()
            for producto in low_stock:
                activity.append({
                    'title': 'Stock bajo',
                    'description': f"{producto.nombre} - {producto.stock} unidades",
                    'timestamp': producto.fecha_creacion.isoformat() if producto.fecha_creacion else None,
                    'icon': '⚠',
                    'icon_class': 'warning'
                })

            recent_users = Usuario.query.order_by(Usuario.fecha_registro.desc()).limit(2).all()
            for usuario in recent_users:
                activity.append({
                    'title': 'Nuevo usuario',
                    'description': usuario.nombre_usuario,
                    'timestamp': usuario.fecha_registro.isoformat() if usuario.fecha_registro else None,
                    'icon': '👤',
                    'icon_class': 'info'
                })

        return jsonify({
            'success': True,
            'activity': activity
        })
    except Exception as e:
        print(f"Error dashboard activity: {e}")
        return jsonify({'success': False, 'error': 'Error al cargar actividad'}), 500


@web_bp.route('/api/admin/dashboard/recent-orders')
@admin_required
def api_admin_dashboard_recent_orders():
    try:
        pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).limit(5).all()
        orders = []
        for pedido in pedidos:
            productos = [item.producto.nombre for item in pedido.items if item.producto]
            resumen = ', '.join(productos[:2]) + (f" y {len(productos) - 2} más" if len(productos) > 2 else '')
            orders.append({
                'numero_pedido': f"#ORD-{pedido.id_pedido:03d}",
                'cliente': pedido.usuario.nombre_usuario if pedido.usuario else 'Cliente',
                'productos': resumen or 'Sin productos',
                'total': float(pedido.total or 0),
                'estado': pedido.estado,
                'estado_label': pedido.estado.capitalize(),
                'fecha': pedido.fecha_pedido.strftime('%Y-%m-%d') if pedido.fecha_pedido else ''
            })

        return jsonify({
            'success': True,
            'orders': orders
        })
    except Exception as e:
        print(f"Error dashboard recent orders: {e}")
        return jsonify({'success': False, 'error': 'Error al cargar pedidos recientes'}), 500

# ----------------------------------------- REPORTES ADMIN ---------------------------------------- #


# ----------------------------------------- UTILIDADES ---------------------------------------- #

def deshabilitar_productos_sin_stock():
    """Deshabilita automáticamente productos cuando el stock llega a 0"""
    try:
        productos_sin_stock = Producto.query.filter(
            Producto.stock == 0,
            Producto.activo == True
        ).all()
        
        for producto in productos_sin_stock:
            producto.activo = False
            print(f"Producto deshabilitado por stock 0: {producto.nombre}")
        
        if productos_sin_stock:
            db.session.commit()
            print(f"Se deshabilitaron {len(productos_sin_stock)} productos sin stock")
            
        return len(productos_sin_stock)
        
    except Exception as e:
        print(f"Error deshabilitando productos sin stock: {e}")
        db.session.rollback()
        return 0

@web_bp.route('/api/admin/limpiar-stock-cero', methods=['POST'])
@admin_required
def api_limpiar_stock_cero():
    """Endpoint para que el admin pueda limpiar manualmente productos sin stock"""
    try:
        cantidad_deshabilitados = deshabilitar_productos_sin_stock()
        
        return jsonify({
            'success': True,
            'message': f'Se deshabilitaron {cantidad_deshabilitados} productos sin stock'
        })
        
    except Exception as e:
        print(f"Error en limpieza de stock: {e}")
        return jsonify({'success': False, 'error': 'Error en limpieza de stock'}), 500

@web_bp.route('/api/admin/productos/validar')
@admin_required
def api_validar_producto():
    """Validar si ya existe un producto con el mismo nombre en la misma categoría"""
    try:
        nombre = request.args.get('nombre', '').strip()
        categoria_id = request.args.get('categoria_id', '')
        excluir_id = request.args.get('excluir_id', '')

        if not nombre or not categoria_id:
            return jsonify({'existe': False})

        # Construir consulta
        query = Producto.query.filter(
            Producto.nombre.ilike(nombre),
            Producto.categoria_id == categoria_id
        )

        # Excluir producto actual en caso de edición
        if excluir_id:
            query = query.filter(Producto.id_producto != excluir_id)

        # Verificar si existe
        producto_existente = query.first()
        existe = producto_existente is not None

        return jsonify({'existe': existe})

    except Exception as e:
        print(f"Error validando producto: {e}")
        return jsonify({'existe': False, 'error': 'Error en validación'}), 500

# ----------------------------------------- RUTAS DE DEBUG ---------------------------------------- #

@web_bp.route('/debug/database')
def debug_database():
    """Ruta para debuggear el estado de la base de datos"""
    try:
        categorias = Categoria.query.all()
        productos = Producto.query.all()
        usuarios = Usuario.query.all()
        roles = Role.query.all()
        
        debug_info = {
            'categorias_count': len(categorias),
            'categorias': [{'id': c.id_categoria, 'nombre': c.nombre} for c in categorias],
            'productos_count': len(productos),
            'productos': [{'id': p.id_producto, 'nombre': p.nombre, 'categoria_id': p.categoria_id} for p in productos],
            'usuarios_count': len(usuarios),
            'usuarios': [{'id': u.id_usuario, 'username': u.nombre_usuario, 'rol_id': u.rol_id} for u in usuarios],
            'roles_count': len(roles),
            'roles': [{'id': r.id_rol, 'nombre': r.nombre} for r in roles]
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_bp.route('/debug/session')
def debug_session():
    """Ruta para debuggear la sesión"""
    return jsonify({
        'session_data': dict(session),
        'user_id_in_session': 'user_id' in session,
        'user_role_in_session': 'user_role' in session
    })

@web_bp.route('/debug/favoritos')
@login_required
def debug_favoritos():
    """Ruta para debuggear favoritos"""
    try:
        usuario_id = session['user_id']
        
        # Contar favoritos del usuario
        count = Favorito.query.filter_by(usuario_id=usuario_id).count()
        
        # Obtener algunos favoritos de ejemplo
        favoritos = Favorito.query.filter_by(usuario_id=usuario_id).limit(5).all()
        
        favoritos_data = []
        for fav in favoritos:
            favoritos_data.append({
                'id_favorito': fav.id_favorito,
                'usuario_id': fav.usuario_id,
                'producto_id': fav.producto_id,
                'fecha_agregado': fav.fecha_agregado.isoformat() if fav.fecha_agregado else None
            })
        
        return jsonify({
            'usuario_actual': usuario_id,
            'total_favoritos': count,
            'favoritos_ejemplo': favoritos_data,
            'tabla_existe': True,
            'estructura': 'id_favorito, usuario_id, producto_id, fecha_agregado'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_bp.route('/api/admin/pedidos/crear-prueba', methods=['POST'])
@admin_required
def api_crear_pedidos_prueba():
    """Crear pedidos de prueba (eliminar en producción)"""
    try:
        from app.models.pedido import Pedido, PedidoItem
        from app.models.usuario import Usuario
        from app.models.models import Producto
        
        # Crear algunos pedidos de prueba
        usuarios = Usuario.query.limit(3).all()
        productos = Producto.query.limit(5).all()
        
        if not usuarios or not productos:
            return jsonify({'success': False, 'error': 'Necesitas usuarios y productos para crear pedidos de prueba'}), 400
        
        estados = ['pendiente', 'procesando', 'completado', 'cancelado']
        
        for i in range(5):
            usuario = usuarios[i % len(usuarios)]
            pedido = Pedido(
                usuario_id=usuario.id_usuario,
                total=0,
                estado=estados[i % len(estados)],
                direccion_envio=f"Dirección de prueba {i+1}"
            )
            db.session.add(pedido)
            db.session.flush()
            
            # Agregar items al pedido
            total_pedido = 0
            for j in range(2):
                producto = productos[(i + j) % len(productos)]
                cantidad = (i + j + 1) % 3 + 1
                precio = float(producto.precio) if producto.precio else 50.00
                total_item = precio * cantidad
                total_pedido += total_item
                
                item = PedidoItem(
                    pedido_id=pedido.id_pedido,
                    producto_id=producto.id_producto,
                    cantidad=cantidad,
                    precio_unitario=precio
                )
                db.session.add(item)
            
            pedido.total = total_pedido
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '5 pedidos de prueba creados exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creando pedidos de prueba: {e}")
        return jsonify({'success': False, 'error': 'Error al crear pedidos de prueba'}), 500