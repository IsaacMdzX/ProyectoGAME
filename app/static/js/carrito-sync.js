// static/js/carrito-sync.js
class CarritoSync {
    constructor() {
        this.isCarritoPage = window.location.pathname.includes('/carrito');
        this.init();
    }

    init() {
        this.actualizarContadorGlobal();
        this.setupEventListeners();
        this.forceBadgePosition();
        
        // En la página del carrito, actualizar más frecuentemente al inicio
        if (this.isCarritoPage) {
            setTimeout(() => this.forceBadgePosition(), 100);
            setTimeout(() => this.forceBadgePosition(), 500);
        }
        
        // Actualizar cada 30 segundos por si hay cambios en otras pestañas
        setInterval(() => this.actualizarContadorGlobal(), 30000);
    }

    async actualizarContadorGlobal() {
        try {
            const response = await fetch('/api/carrito/cantidad');
            const data = await response.json();
            
            if (data.count !== undefined) {
                this.actualizarBadges(data.count);
                this.forceBadgePosition();
            }
        } catch (error) {
            console.log('Error sincronizando carrito:', error);
        }
    }

    actualizarBadges(count) {
        // Actualizar todos los badges en la página
        const badges = document.querySelectorAll('.carrito-count');
        
        badges.forEach(badge => {
            badge.textContent = count;
            if (badge.style.display === 'none') {
                badge.style.display = 'flex';
            }
        });

        // También actualizar cualquier otro contador con clases diferentes
        const otrosContadores = document.querySelectorAll('.cart-count, #carrito-contador');
        otrosContadores.forEach(contador => {
            contador.textContent = count;
            contador.style.display = count > 0 ? 'inline' : 'none';
        });

        this.forceBadgePosition();
    }

    forceBadgePosition() {
        // Forzar la posición correcta de los badges
        const badges = document.querySelectorAll('.carrito-count');
        badges.forEach(badge => {
            badge.style.position = 'absolute';
            badge.style.top = '-8px';
            badge.style.right = '-8px';
            badge.style.zIndex = '1001';
        });

        // Asegurar que los contenedores tengan posición relativa
        const carritoLinks = document.querySelectorAll('.carrito-link, .icon[href="/carrito"]');
        carritoLinks.forEach(link => {
            link.style.position = 'relative';
            link.style.display = 'inline-flex';
            link.style.alignItems = 'center';
            link.style.justifyContent = 'center';
        });
    }

    setupEventListeners() {
        // Escuchar eventos personalizados de actualización del carrito
        document.addEventListener('carritoActualizado', (event) => {
            if (event.detail && event.detail.count !== undefined) {
                this.actualizarBadges(event.detail.count);
            }
        });

        // También escuchar cambios de storage (para sincronizar entre pestañas)
        window.addEventListener('storage', (event) => {
            if (event.key === 'carritoUpdate') {
                this.actualizarContadorGlobal();
            }
        });

        // Forzar posición cuando cambia la visibilidad de la página
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                setTimeout(() => this.forceBadgePosition(), 100);
            }
        });

        // Forzar posición cuando se hace resize
        window.addEventListener('resize', () => {
            setTimeout(() => this.forceBadgePosition(), 100);
        });
    }

    // Método para notificar a otras pestañas
    notificarActualizacion() {
        localStorage.setItem('carritoUpdate', Date.now().toString());
        setTimeout(() => {
            localStorage.removeItem('carritoUpdate');
        }, 100);
    }
}

// Función global para actualizar el contador desde otros scripts
window.actualizarContadorCarrito = function(count) {
    const badges = document.querySelectorAll('.carrito-count, .cart-count');
    badges.forEach(badge => {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
        // Forzar estilos
        badge.style.position = 'absolute';
        badge.style.top = '-8px';
        badge.style.right = '-8px';
        badge.style.zIndex = '1001';
    });
    
    // Disparar evento personalizado
    document.dispatchEvent(new CustomEvent('carritoActualizado', { 
        detail: { count } 
    }));
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.carritoSync = new CarritoSync();
    
    // Forzar posición adicional después de que todo cargue
    setTimeout(() => {
        if (window.carritoSync) {
            window.carritoSync.forceBadgePosition();
        }
    }, 1000);
});

// También forzar cuando la página termina de cargar completamente
window.addEventListener('load', function() {
    setTimeout(() => {
        if (window.carritoSync) {
            window.carritoSync.forceBadgePosition();
        }
    }, 500);
});