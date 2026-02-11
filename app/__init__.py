from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
import os
import atexit

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

#------------------------------------ Scheduler para mantener la BD activa
scheduler = BackgroundScheduler()

def keep_db_alive():
    """Ejecuta una query simple cada 4 minutos para mantener activa la BD de Neon"""
    try:
        db.session.execute(db.text('SELECT 1'))
        db.session.commit()
        print("✅ Ping a BD ejecutado - Neon activa")
    except Exception as e:
        print(f"⚠️ Error en ping a BD: {e}")
###-------------------------------------------------------
def create_app():
    app = Flask(__name__)
    
    # Configuración según entorno
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object('app.config.ProductionConfig')
        # Configuración importante para producción
        app.config.update(
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
        )
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # Asegurar la clave secreta
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key-for-dev')

    # Ajuste para SQLite: evitar sslmode en connect_args
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite'):
        engine_options = dict(app.config.get('SQLALCHEMY_ENGINE_OPTIONS') or {})
        engine_options.pop('connect_args', None)
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'web.login'
    
    # Registrar blueprints
    from app.routes.web import web_bp
    from app.carrito.routes import carrito_bp
    
    # Registrar nuevos blueprints para API
    from app.api.productos import bp as productos_bp
    from app.api.carrito import bp as carrito_api_bp
    from app.api.auth import bp as auth_bp
    from app.api.mercadopago import bp as mercadopago_bp
    
    app.register_blueprint(web_bp)
    app.register_blueprint(carrito_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(carrito_api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mercadopago_bp)
    
    print("✅ Blueprints registrados: Web, Carrito, Productos, Auth, MercadoPago")
    
    # Configurar user_loader para Flask-Login
    from app.models.usuario import Usuario 
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Solo crear tablas si no existen (sin insertar datos)
    with app.app_context():
        try:
            db.create_all()
            print(" Tablas de base de datos verificadas")

            # Seed de categorías por defecto si no existen
            from app.models.models import Categoria
            if Categoria.query.count() == 0:
                categorias_default = [
                    ("Consolas", "Consolas y hardware"),
                    ("Juegos", "Videojuegos"),
                    ("Accesorios", "Accesorios y periféricos"),
                    ("Controles", "Mandos y controladores"),
                ]
                for nombre, descripcion in categorias_default:
                    db.session.add(Categoria(nombre=nombre, descripcion=descripcion))
                db.session.commit()
                print("✅ Categorías por defecto creadas")
        except Exception as e:
            print(f" Error creando tablas: {e}")
    
    # Iniciar scheduler para mantener BD activa (solo si no está corriendo)
    if not scheduler.running:
        with app.app_context():
            # Agregar job que se ejecuta cada 4 minutos
            scheduler.add_job(
                func=lambda: keep_db_alive(),
                trigger="interval",
                minutes=4,
                id='keep_neon_alive',
                name='Mantener BD Neon activa',
                replace_existing=True
            )
            scheduler.start()
            print("✅ Scheduler iniciado - BD Neon se mantendrá activa")
            
            # Asegurar que el scheduler se detenga cuando la app se cierre
            atexit.register(lambda: scheduler.shutdown())
    
    return app

if __name__ == '__main__':
    # Esto crea la app usando el factory y la ejecuta cuando se ejecuta este módulo directamente
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)