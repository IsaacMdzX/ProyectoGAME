from flask import Blueprint, jsonify, session
from app.models.usuario import Usuario

bp = Blueprint('auth', __name__)

@bp.route('/api/usuario/actual', methods=['GET'])
def usuario_actual():
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
        return jsonify({'error': 'No autenticado'}), 401
    except Exception as e:
        print(f"Error en usuario_actual: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500