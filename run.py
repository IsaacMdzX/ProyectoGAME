from app import create_app

app = create_app()


if __name__ == '__main__':
    # Esto crea la app usando el factory y la ejecuta cuando se ejecuta este módulo directamente
    app.run(host='0.0.0.0', port=5000, debug=True)