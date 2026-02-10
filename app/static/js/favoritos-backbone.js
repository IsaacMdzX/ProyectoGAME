// app/static/js/favoritos-backbone.js - VERSIÓN MEJORADA Y CORREGIDA
class FavoritosManager {
    constructor() {
        this.favoritos = new Set();
        this.isAuthenticated = false;
        this.init();
    }

    async init() {
        console.log('FavoritosManager inicializado');
        await this.checkAuth();
        this.setupEventListeners();
        
        if (window.location.pathname === '/favoritos') {
            this.loadFavoritosPage();
        } else {
            this.syncFavoritos();
        }
    }

    async checkAuth() {
        try {
            const response = await fetch('/api/user-info');
            const data = await response.json();
            this.isAuthenticated = data.logged_in;
            return this.isAuthenticated;
        } catch (error) {
            console.error('Error verificando autenticación:', error);
            return false;
        }
    }

    setupEventListeners() {
        // Evento para botones de favorito en TODA la página
        document.addEventListener('click', (e) => {
            const favoritoBtn = e.target.closest('.favorito-btn');
            if (favoritoBtn) {
                e.preventDefault();
                e.stopPropagation();
                const productId = favoritoBtn.getAttribute('data-product-id');
                if (productId) {
                    this.toggleFavorito(productId, favoritoBtn);
                }
            }

            // Evento para agregar al carrito desde favoritos
            const carritoBtn = e.target.closest('.btn-agregar-carrito');
            if (carritoBtn) {
                e.preventDefault();
                const productId = carritoBtn.getAttribute('data-id');
                if (productId) {
                    this.agregarAlCarritoDesdeFavoritos(productId, carritoBtn);
                }
            }
        });
    }

    async verificarAutenticacion() {
        if (this.isAuthenticated) return true;
        
        try {
            const response = await fetch('/api/user-info');
            const data = await response.json();
            this.isAuthenticated = data.logged_in;
            return this.isAuthenticated;
        } catch (error) {
            console.error('Error verificando autenticación:', error);
            return false;
        }
    }

    async toggleFavorito(productId, button) {
        const autenticado = await this.verificarAutenticacion();
        
        if (!autenticado) {
            this.showNotification('Inicia sesion para poder agregar productos a favoritos', 'error');
            
            return;
        }

        const isFavorito = button.classList.contains('active');
        
        try {
            button.disabled = true;
            
            if (isFavorito) {
                await this.removeFavorito(productId, button);
            } else {
                await this.addFavorito(productId, button);
            }
        } catch (error) {
            console.error('Error en toggleFavorito:', error);
            this.showNotification('Error al actualizar favoritos', 'error');
        } finally {
            button.disabled = false;
        }
    }

    async addFavorito(productId, button) {
        try {
            const response = await fetch('/api/favoritos/agregar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ producto_id: parseInt(productId) })
            });

            const data = await response.json();

            if (data.success) {
                this.favoritos.add(parseInt(productId));
                this.updateFavoritoButtons(productId, true);
                
                // Solo mostrar notificación si no estamos en la página de favoritos
                if (window.location.pathname !== '/favoritos') {
                    this.showNotification('Producto agregado a favoritos', 'success');
                }
                
                // Si estamos en favoritos, recargar la página
                if (window.location.pathname === '/favoritos') {
                    this.loadFavoritosPage();
                }
            } else {
                console.error('Error agregando favorito:', data.error);
            }
        } catch (error) {
            console.error('Error agregando favorito:', error);
        }
    }

    async removeFavorito(productId, button) {
        try {
            const response = await fetch(`/api/favoritos/eliminar/${productId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.favoritos.delete(parseInt(productId));
                this.updateFavoritoButtons(productId, false);
                
                // Solo mostrar notificación si no estamos en la página de favoritos
                if (window.location.pathname !== '/favoritos') {
                    this.showNotification('Producto eliminado de favoritos', 'success');
                }
                
                // Si estamos en favoritos, recargar la página
                if (window.location.pathname === '/favoritos') {
                    this.loadFavoritosPage();
                }
            } else {
                console.error('Error eliminando favorito:', data.error);
            }
        } catch (error) {
            console.error('Error eliminando favorito:', error);
        }
    }

    updateFavoritoButtons(productId, isFavorito) {
        const buttons = document.querySelectorAll(`.favorito-btn[data-product-id="${productId}"]`);
        buttons.forEach(button => {
            if (isFavorito) {
                button.classList.add('active');
                button.innerHTML = '<i class="fa-solid fa-heart"></i>';
            } else {
                button.classList.remove('active');
                button.innerHTML = '<i class="fa-regular fa-heart"></i>';
            }
        });
    }

    async loadFavoritosPage() {
        if (!this.isAuthenticated) {
            this.showNotAuthenticated();
            return;
        }

        const container = document.getElementById('favoritos-container');
        if (!container) return;

        container.innerHTML = '<div class="loading"><i class="fa-solid fa-spinner fa-spin"></i> Cargando favoritos...</div>';

        try {
            const response = await fetch('/api/favoritos');
            const data = await response.json();

            if (data.success) {
                this.favoritos = new Set(data.favoritos.map(f => f.producto.id));
                this.renderFavoritos(data.favoritos);
            } else {
                this.showError(data.error || 'Error al cargar favoritos');
            }
        } catch (error) {
            console.error('Error cargando favoritos:', error);
            this.showError('Error de conexión');
        }
    }

    renderFavoritos(favoritos) {
        const container = document.getElementById('favoritos-container');
        if (!container) return;

        if (favoritos.length === 0) {
            container.innerHTML = this.getEmptyFavoritesHTML();
            return;
        }

        container.innerHTML = favoritos.map(favorito => `
            <div class="producto" data-id="${favorito.producto.id}">
                <button class="favorito-btn active" data-product-id="${favorito.producto.id}">
                    <i class="fa-solid fa-heart"></i>
                </button>
                
                <img src="${favorito.producto.imagen || '/static/img/placeholder.jpg'}" 
                     alt="${favorito.producto.nombre}" 
                     onerror="this.src='/static/img/placeholder.jpg'">
                <h3>${favorito.producto.nombre}</h3>
                <p class="categoria">${favorito.producto.categoria}</p>
                <p class="descripcion">${favorito.producto.descripcion}</p>
                <p class="precio">$${favorito.producto.precio.toFixed(2)}</p>
                <button class="btn-agregar-carrito" 
                        data-id="${favorito.producto.id}"
                        ${favorito.producto.stock === 0 ? 'disabled' : ''}>
                    ${favorito.producto.stock === 0 ? 'Sin Stock' : '<i class="fa-solid fa-cart-shopping"></i> Agregar al Carrito'}
                </button>
            </div>
        `).join('');

        this.setupCarritoEventListeners();
    }

    setupCarritoEventListeners() {
        document.addEventListener('click', (e) => {
            const carritoBtn = e.target.closest('.btn-agregar-carrito');
            if (carritoBtn) {
                e.preventDefault();
                const productId = carritoBtn.getAttribute('data-id');
                if (productId) {
                    this.agregarAlCarritoDesdeFavoritos(productId, carritoBtn);
                }
            }
        });
    }

async agregarAlCarritoDesdeFavoritos(productId, button) {
    // ✅ PREVENIR MÚLTIPLES CLICKS
    if (button.disabled) {
        console.log('⏳ Botón ya en proceso, ignorando click');
        return;
    }
    
    try {
        // Deshabilitar botón temporalmente
        button.disabled = true;
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> AGREGANDO...';
        
        console.log(`🛒 Agregando producto ${productId} al carrito desde favoritos`);

        const response = await fetch('/api/carrito/agregar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                producto_id: parseInt(productId),
                cantidad: 1
            })
        });

        const data = await response.json();
        console.log('📨 Respuesta del servidor:', data);

        if (data.success) {
            this.showNotification(data.message, 'success');
            
            // Actualizar contador del carrito
            if (window.carritoSimple) {
                window.carritoSimple.actualizarContadorCarrito();
            }
            
            // Si estamos en la página del carrito, recargar
            if (window.carritoDinamico && document.getElementById('carrito-container')) {
                await window.carritoDinamico.cargarCarrito();
                window.carritoDinamico.actualizarVistaCarrito();
            }
        } else {
            this.showNotification(data.error || 'Error al agregar al carrito', 'error');
        }
    } catch (error) {
        console.error('❌ Error agregando al carrito:', error);
        this.showNotification('Error de conexión', 'error');
    } finally {
        // ✅ GARANTIZAR QUE EL BOTÓN SIEMPRE SE RESTAURE
        button.disabled = false;
        
        // Restaurar texto original basado en stock
        const tieneStock = !button.hasAttribute('data-sin-stock');
        if (tieneStock) {
            button.innerHTML = '<i class="fa-solid fa-cart-shopping"></i> AGREGAR AL CARRITO';
        } else {
            button.innerHTML = 'SIN STOCK';
            button.disabled = true;
        }
    }
}

    async syncFavoritos() {
        if (!this.isAuthenticated) return;

        try {
            const response = await fetch('/api/favoritos');
            const data = await response.json();

            if (data.success) {
                this.favoritos = new Set(data.favoritos.map(f => f.producto.id));
                this.marcarFavoritosEnPagina(data.favoritos);
            }
        } catch (error) {
            console.error('Error sincronizando favoritos:', error);
        }
    }

    marcarFavoritosEnPagina(favoritos) {
        favoritos.forEach(favorito => {
            const productId = favorito.producto.id;
            const buttons = document.querySelectorAll(`.favorito-btn[data-product-id="${productId}"]`);
            
            buttons.forEach(button => {
                button.classList.add('active');
                button.innerHTML = '<i class="fa-solid fa-heart"></i>';
            });
        });
    }

    marcarFavoritosExistentes() {
        if (!this.isAuthenticated) return;
        
        fetch('/api/favoritos')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.marcarFavoritosEnPagina(data.favoritos);
                }
            })
            .catch(error => {
                console.error('Error marcando favoritos:', error);
            });
    }

    showNotAuthenticated() {
        const container = document.getElementById('favoritos-container');
        if (container) {
            container.innerHTML = `
                <div class="no-autenticado">
                    <i class="fa-solid fa-user-lock"></i>
                    <h3>Inicia sesión para ver tus favoritos</h3>
                    <p>Necesitas tener una cuenta para guardar productos en favoritos</p>
                    <div class="acciones-auth">
                        <a href="/login?redirect=${encodeURIComponent(window.location.pathname)}" class="btn-login">Iniciar Sesión</a>
                        <a href="/registro" class="btn-registro">Crear Cuenta</a>
                    </div>
                </div>
            `;
        }
    }

    getEmptyFavoritesHTML() {
        return `
            <div class="no-favoritos">
                <i class="fa-regular fa-heart"></i>
                <h3>No tienes productos favoritos</h3>
                <p>Agrega algunos productos a tus favoritos para verlos aquí</p>
                <a href="/" class="btn-seguir-comprando">Descubrir productos</a>
            </div>
        `;
    }

    showError(mensaje) {
        const container = document.getElementById('favoritos-container');
        if (container) {
            container.innerHTML = `
                <div class="error">
                    <i class="fa-solid fa-exclamation-triangle"></i>
                    <h3>Error</h3>
                    <p>${mensaje}</p>
                    <button onclick="window.favoritosManager.loadFavoritosPage()" class="btn-reintentar">
                        Reintentar
                    </button>
                </div>
            `;
        }
    }

    showNotification(message, type) {
        if (window.carritoSimple && window.carritoSimple.mostrarNotificacion) {
            window.carritoSimple.mostrarNotificacion(message, type);
        } else {
            const notification = document.createElement('div');
            notification.className = `notification-custom ${type}`;
            notification.innerHTML = `
                <div class="notification-content">
                    <i class="fa-solid fa-${type === 'success' ? 'check' : 'exclamation'}"></i>
                    <span>${message}</span>
                </div>
            `;
            
            document.body.appendChild(notification);
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 3000);
        }
    }
}

// Inicializar en TODAS las páginas
document.addEventListener('DOMContentLoaded', function() {
    window.favoritosManager = new FavoritosManager();
});

// Función global para forzar sincronización
window.forceSyncFavoritos = function() {
    if (window.favoritosManager) {
        window.favoritosManager.syncFavoritos();
    }
};