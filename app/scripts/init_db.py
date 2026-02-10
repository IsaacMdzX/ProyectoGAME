import os
from app import create_app, db
from app.models.role import Role
from app.models.usuario import Usuario
from app.models.analytics import AdminActivity, InventarioMovimiento, Pago, Reporte, ReporteItem
from werkzeug.security import generate_password_hash


def seed_roles():
    roles = [
        (1, "Administrador"),
        (2, "Cliente"),
    ]
    for role_id, nombre in roles:
        role = Role.query.get(role_id)
        if not role:
            db.session.add(Role(id_rol=role_id, nombre=nombre))
    db.session.commit()


def seed_admin():
    admin_user = os.environ.get("ADMIN_USER")
    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")

    if not (admin_user and admin_email and admin_password):
        return

    existing = Usuario.query.filter(
        (Usuario.correo == admin_email) | (Usuario.nombre_usuario == admin_user)
    ).first()
    if existing:
        return

    hashed = generate_password_hash(admin_password)
    nuevo_admin = Usuario(
        nombre=admin_user,
        correo=admin_email,
        nombre_usuario=admin_user,
        password=hashed,
        rol_id=1,
        activo=True,
    )
    db.session.add(nuevo_admin)
    db.session.commit()


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_roles()
        seed_admin()
        print("✅ Base de datos creada y roles iniciales cargados")
        if os.environ.get("ADMIN_USER"):
            print("✅ Admin creado (si no existía)")


if __name__ == "__main__":
    main()
