from flask import Blueprint, request, jsonify, current_app
import mercadopago

bp = Blueprint('mercadopago_api', __name__)


def get_mp_client():
    token = current_app.config.get('MERCADOPAGO_ACCESS_TOKEN')
    if not token:
        raise RuntimeError('MERCADOPAGO_ACCESS_TOKEN no configurado en la aplicacion')
    return mercadopago.SDK(token)


@bp.route('/api/mercadopago/config', methods=['GET'])
def mp_config():
    """Devolver configuración pública necesaria para el cliente (public_key)."""
    try:
        public_key = current_app.config.get('MERCADOPAGO_PUBLIC_KEY', '')
        return jsonify({'public_key': public_key})
    except Exception as e:
        print(f"Error obteniendo config Mercado Pago: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@bp.route('/api/mercadopago/preference', methods=['POST'])
def create_preference():
    """Crear una preference de Mercado Pago y devolver init_point.

    Espera JSON con clave `items`: lista de objetos {title, quantity, unit_price}
    Opcional: `back_urls` dict con success/failure/pending.
    """
    try:
        payload = request.get_json(force=True)
        items = payload.get('items')
        if not items or not isinstance(items, list):
            return jsonify({'error': 'items es requerido y debe ser una lista'}), 400

        back_urls = payload.get('back_urls')
        if not back_urls:
            host = request.host_url.rstrip('/')
            back_urls = {
                'success': f"{host}/pago_exitoso",
                'failure': f"{host}/pago_cancelado",
                'pending': f"{host}/pago_cancelado"
            }

        preference_data = {
            'items': items,
            'back_urls': back_urls,
            'auto_return': 'approved'
        }

        # Si se proporciona un pedido_id, setear external_reference para asociar la preference al pedido
        pedido_id = payload.get('pedido_id')
        if pedido_id:
            preference_data['external_reference'] = str(pedido_id)

        mp = get_mp_client()
        preference_response = mp.preference().create(preference_data)

        # SDK devuelve dict con 'status' y 'response'
        resp = preference_response
        # Mantener logging y formato similar al resto del proyecto
        print(f"✅ Preference creada: status={resp.get('status')}")
        return jsonify(resp.get('response', {}))

    except RuntimeError as e:
        print(f"Error en Mercado Pago config: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        print(f"Error creando preference Mercado Pago: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500


@bp.route('/api/mercadopago/webhook', methods=['POST'])
def webhook():
    """Endpoint simple para recibir notificaciones de Mercado Pago.

    Se recomienda verificar la firma o consultar la API de Mercado Pago para validar el evento.
    """
    try:
        data = request.get_json(force=True)
        print('MP Webhook recibido:', data)

        # Obtener el id del pago según el formato de notificación
        payment_id = None
        # Algunos webhooks vienen como {"data": {"id": ...}, "type": "payment"}
        if isinstance(data, dict):
            if 'data' in data and isinstance(data['data'], dict):
                payment_id = data['data'].get('id')
            if not payment_id:
                # Otros formatos pueden usar 'id' directamente
                payment_id = data.get('id')

        if not payment_id:
            print('MP Webhook: no se encontró payment id en el payload')
            return jsonify({'status': 'ignored', 'reason': 'no payment id'}), 200

        # Consultar la API de Mercado Pago para validar el pago
        try:
            mp = get_mp_client()
            payment_resp = mp.payment().get(payment_id)
            payment_data = payment_resp.get('response') if isinstance(payment_resp, dict) else None
        except Exception as e:
            print(f"Error consultando API de Mercado Pago para payment {payment_id}: {e}")
            payment_data = None

        status = None
        if payment_data:
            status = payment_data.get('status') or payment_data.get('collection_status')
            print(f"MP Payment {payment_id} status: {status}")

        # Si el pago está aprobado, actualizar el pedido correspondiente
        if status and status.lower() in ('approved', 'approved_by_merchant'):
            from app.models.pedido import Pedido, PedidoItem
            from app.models.models import Producto, Carrito, CarritoItem
            from app import db

            pedido = Pedido.query.filter_by(id_transaccion_mercadopago=str(payment_id)).first()

            # Si no lo encontramos por id_transaccion, intentar por external_reference
            external_ref = None
            if payment_data:
                external_ref = payment_data.get('external_reference') or (
                    payment_data.get('order', {}) or {}).get('external_reference')

            if not pedido and external_ref:
                try:
                    # external_reference fue seteado como el id del pedido (string)
                    pedido = Pedido.query.get(int(external_ref))
                except Exception:
                    pedido = Pedido.query.filter_by(id_pedido=external_ref).first()

            if pedido:
                if pedido.estado != 'completado':
                    # Guardar id_transaccion_mercadopago si no existe
                    if not pedido.id_transaccion_mercadopago:
                        pedido.id_transaccion_mercadopago = str(payment_id)

                    # Reducir stock de los productos del pedido
                    try:
                        for item in pedido.items:
                            producto = Producto.query.get(item.producto_id)
                            if producto:
                                producto.stock = (producto.stock or 0) - (item.cantidad or 0)
                                if producto.stock <= 0:
                                    producto.activo = False

                        # Limpiar carrito activo del usuario (si existe)
                        carrito = Carrito.query.filter_by(usuario_id=pedido.usuario_id, activo=True).first()
                        if carrito:
                            for ci in list(carrito.items):
                                db.session.delete(ci)
                            carrito.activo = False

                        pedido.estado = 'completado'
                        db.session.commit()
                        print(f"Pedido {pedido.id_pedido} marcado como completado por webhook MP y stock actualizado")
                    except Exception as e:
                        print(f"Error finalizando pedido {pedido.id_pedido}: {e}")
                        db.session.rollback()
            else:
                print(f"No se encontró pedido con id_transaccion_mercadopago={payment_id} ni por external_reference={external_ref}")

        return jsonify({'status': 'received'}), 200

    except Exception as e:
        print(f"Error en webhook Mercado Pago: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500
