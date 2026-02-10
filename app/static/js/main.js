// Punto de entrada de la aplicación Backbone
$(document).ready(function() {
    console.log('🎮 Inicializando GameStore con Backbone...');

    // Crear instancia global de productos
    window.app = {
        productos: new Productos(),
        vistas: {}
    };

    // Cargar datos iniciales de productos
    window.app.productos.fetch({
        success: function(collection) {
            console.log(`✅ ${collection.length} productos cargados`);
            
            // Inicializar la aplicación principal
            inicializarAplicacion();
        },
        error: function(collection, response) {
            console.error('❌ Error cargando productos:', response);
            
            // Cargar datos de ejemplo si hay error
            cargarDatosEjemplo();
        }
    });

    function inicializarAplicacion() {
        console.log('🚀 Inicializando vistas...');
        
        // Renderizar todos los productos
        renderizarProductos();
        
        // Inicializar otras funcionalidades
        inicializarBusqueda();
        inicializarFiltros();
        
        console.log('✅ GameStore Backbone inicializado correctamente');
    }

    function renderizarProductos() {
        const $contenedor = $('.productos');
        $contenedor.empty();
        
        window.app.productos.each(function(producto) {
            const productoView = new ProductoView({ model: producto });
            $contenedor.append(productoView.render().el);
            
            // Escuchar eventos de la vista
            productoView.on('producto:agregarCarrito', function(model) {
                console.log('Agregar al carrito:', model.get('nombre'));
                // Aquí conectarás con el carrito después
            });
            
            productoView.on('producto:toggleFavorito', function(model, esFavorito) {
                console.log('Favorito:', model.get('nombre'), esFavorito);
                // Aquí conectarás con favoritos después
            });
        });
    }

    function inicializarBusqueda() {
        console.log('🔍 Inicializando búsqueda...');
        // Inicializarás después
    }

    function inicializarFiltros() {
        console.log('🎛️ Inicializando filtros...');
        // Inicializarás después
    }

    function cargarDatosEjemplo() {
        console.log('📦 Cargando datos de ejemplo...');
        
        const datosEjemplo = [
            {
                id: 1,
                nombre: 'XBOX SERIES X 2TB GALAXY BLACK',
                precio: 17000.00,
                categoria: 'consolas',
                imagen: '/static/img/Imagenes/series_x_especial.png',
                descripcion: 'Consola Xbox Series X edición especial',
                enStock: true,
                esFavorito: false
            },
            {
                id: 2,
                nombre: 'AUDÍFONOS GAMER',
                precio: 760.00,
                categoria: 'accesorios',
                imagen: '/static/img/Imagenes/Audifonos_Gamer.jpg',
                descripcion: 'Audífonos gaming profesionales',
                enStock: true,
                esFavorito: false
            },
            {
                id: 3,
                nombre: 'CONTROL XBOX INALÁMBRICO WHITE',
                precio: 1496.99,
                categoria: 'controles',
                imagen: '/static/img/Imagenes/controlxboxwhite.png',
                descripcion: 'Control inalámbrico para Xbox',
                enStock: true,
                esFavorito: false
            }
        ];
        
        window.app.productos.reset(datosEjemplo);
        inicializarAplicacion();
    }
});