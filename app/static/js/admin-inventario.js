class AdminInventario {
    constructor() {
        this.productos = [];
        this.categorias = [];
        this.init();
    }

    async init() {
        await this.cargarCategorias();
        await this.cargarProductos();
        this.initEventListeners();
        this.actualizarEstadisticas();
    }

    async cargarCategorias() {
        try {
            const response = await fetch('/api/categorias', {
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`Respuesta inválida (${response.status})`);
            }

            const data = await response.json();

            if (data.success && Array.isArray(data.categorias)) {
                this.categorias = data.categorias;
                this.actualizarSelectCategorias();
                console.log(`✅ ${this.categorias.length} categorías cargadas`);
                return;
            }

            throw new Error('Respuesta sin categorías');
        } catch (error) {
            console.error('❌ Error cargando categorías:', error);
            this.categorias = [];
            this.actualizarSelectCategorias(true);
            this.mostrarNotificacion('No se pudieron cargar las categorías', 'error');
        }
    }

    async cargarProductos(filtros = {}) {
        try {
            let url = '/api/admin/productos';
            const params = new URLSearchParams();
            
            if (filtros.search) params.append('search', filtros.search);
            if (filtros.categoria) params.append('categoria', filtros.categoria);
            if (filtros.estado) params.append('estado', filtros.estado);
            
            if (params.toString()) {
                url += '?' + params.toString();
            }

            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success) {
                this.productos = data.productos;
                this.mostrarProductos();
                this.actualizarEstadisticas();
                console.log(`✅ ${this.productos.length} productos cargados`);
            }
        } catch (error) {
            console.error('❌ Error cargando productos:', error);
            this.mostrarNotificacion('Error al cargar los productos', 'error');
        }
    }

    mostrarProductos() {
        const tbody = document.getElementById('productos-body');
        
        if (this.productos.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="no-data">
                        <i class="fa-solid fa-box-open"></i>
                        <p>No se encontraron productos</p>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.productos.map(producto => `
            <tr data-id="${producto.id}">
                <td class="producto-imagen">
                    <img src="${producto.imagen || '/static/img/placeholder.jpg'}" 
                         alt="${producto.nombre}"
                         onerror="this.src='/static/img/placeholder.jpg'">
                </td>
                <td class="producto-nombre">
                    <strong>${producto.nombre}</strong>
                    <small>${producto.descripcion || 'Sin descripción'}</small>
                </td>
                <td class="producto-categoria">${producto.categoria}</td>
                <td class="producto-precio">$${parseFloat(producto.precio).toFixed(2)}</td>
                <td class="producto-stock">
                    <span class="stock-badge ${producto.stock < 10 ? 'bajo' : producto.stock < 20 ? 'medio' : 'alto'}">
                        ${producto.stock}
                    </span>
                </td>
                <td class="producto-estado">
                    <span class="estado-badge ${producto.activo ? 'activo' : 'inactivo'}">
                        <i class="fa-solid fa-${producto.activo ? 'check' : 'times'}"></i>
                        ${producto.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td class="producto-acciones">
                    <button class="btn-editar" onclick="adminInventario.editarProducto(${producto.id})">
                        <i class="fa-solid fa-edit"></i> Editar
                    </button>
                    <button class="btn-${producto.activo ? 'desactivar' : 'activar'}" 
                            onclick="adminInventario.toggleEstado(${producto.id}, ${!producto.activo})">
                        <i class="fa-solid fa-${producto.activo ? 'eye-slash' : 'eye'}"></i>
                        ${producto.activo ? 'Desactivar' : 'Activar'}
                    </button>
                    <button class="btn-eliminar" onclick="adminInventario.eliminarProducto(${producto.id})">
                        <i class="fa-solid fa-trash"></i> Eliminar
                    </button>
                </td>
            </tr>
        `).join('');
    }

    actualizarEstadisticas() {
        const total = this.productos.length;
        const activos = this.productos.filter(p => p.activo).length;
        const inactivos = total - activos;
        const stockBajo = this.productos.filter(p => p.stock < 10).length;

        document.getElementById('total-productos').textContent = total;
        document.getElementById('productos-activos').textContent = activos;
        document.getElementById('productos-inactivos').textContent = inactivos;
        document.getElementById('stock-bajo').textContent = stockBajo;
    }

    actualizarSelectCategorias(falloCarga = false) {
        const selectCategoria = document.getElementById('producto-categoria');
        const filtroCategoria = document.getElementById('filtro-categoria');

        if (!selectCategoria || !filtroCategoria) {
            return;
        }

        if (this.categorias.length === 0) {
            const mensaje = falloCarga ? 'No se pudieron cargar' : 'No hay categorías';
            selectCategoria.innerHTML = `<option value="">${mensaje}</option>`;
            filtroCategoria.innerHTML = `<option value="">${mensaje}</option>`;
            return;
        }

        const options = '<option value="">Seleccionar categoría</option>' +
            this.categorias.map(cat =>
                `<option value="${cat.id}">${cat.nombre}</option>`
            ).join('');

        selectCategoria.innerHTML = options;
        filtroCategoria.innerHTML = '<option value="">Todas las categorías</option>' +
            this.categorias.map(cat =>
                `<option value="${cat.id}">${cat.nombre}</option>`
            ).join('');
    }

    initEventListeners() {
        console.log('🔄 Inicializando event listeners...');
        
        setTimeout(() => {
            // Botón agregar producto
            const btnAgregar = document.getElementById('btn-agregar-producto');
            console.log('🔘 Botón agregar producto encontrado:', btnAgregar);
            
            if (btnAgregar) {
                btnAgregar.addEventListener('click', () => {
                    console.log('🎯 Click en agregar producto');
                    this.mostrarModal();
                });
            }

            // Buscador
            const searchBtn = document.getElementById('search-btn-admin');
            const searchInput = document.getElementById('search-admin');
            
            if (searchBtn && searchInput) {
                searchBtn.addEventListener('click', () => {
                    this.aplicarFiltros();
                });

                searchInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        this.aplicarFiltros();
                    }
                });
            }

            // Filtros
            const filtroCategoria = document.getElementById('filtro-categoria');
            const filtroEstado = document.getElementById('filtro-estado');
            
            if (filtroCategoria) {
                filtroCategoria.addEventListener('change', () => {
                    this.aplicarFiltros();
                });
            }
            
            if (filtroEstado) {
                filtroEstado.addEventListener('change', () => {
                    this.aplicarFiltros();
                });
            }

            // Modal
            const modalCerrar = document.getElementById('modal-cerrar');
            const btnCancelar = document.getElementById('btn-cancelar');
            const formProducto = document.getElementById('form-producto');
            
            if (modalCerrar) {
                modalCerrar.addEventListener('click', () => {
                    this.ocultarModal();
                });
            }
            
            if (btnCancelar) {
                btnCancelar.addEventListener('click', () => {
                    this.ocultarModal();
                });
            }
            
            if (formProducto) {
                formProducto.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.guardarProducto();
                });
            }

            // Validación en tiempo real del nombre
            const inputNombre = document.getElementById('producto-nombre');
            if (inputNombre) {
                inputNombre.addEventListener('blur', () => {
                    this.validarNombreEnTiempoReal();
                });
            }

            console.log('✅ Event listeners inicializados correctamente');
        }, 100);
    }

    aplicarFiltros() {
        const search = document.getElementById('search-admin').value;
        const categoria = document.getElementById('filtro-categoria').value;
        const estado = document.getElementById('filtro-estado').value;

        this.cargarProductos({ search, categoria, estado });
    }

    mostrarModal(producto = null) {
        const modal = document.getElementById('modal-producto');
        const titulo = document.getElementById('modal-titulo');
        const form = document.getElementById('form-producto');
        
        if (producto) {
            titulo.textContent = 'Editar Producto';
            this.cargarDatosFormulario(producto);
        } else {
            titulo.textContent = 'Agregar Producto';
            form.reset();
            document.getElementById('producto-id').value = '';
            this.limpiarErroresFormulario();
        }
        
        modal.style.display = 'block';
    }

    ocultarModal() {
        document.getElementById('modal-producto').style.display = 'none';
        this.limpiarErroresFormulario();
    }

    cargarDatosFormulario(producto) {
        document.getElementById('producto-id').value = producto.id;
        document.getElementById('producto-nombre').value = producto.nombre;
        document.getElementById('producto-descripcion').value = producto.descripcion || '';
        document.getElementById('producto-precio').value = parseFloat(producto.precio).toFixed(2);
        document.getElementById('producto-stock').value = producto.stock;
        document.getElementById('producto-categoria').value = producto.categoria_id;
        document.getElementById('producto-imagen').value = producto.imagen || '';
        document.getElementById('producto-activo').checked = producto.activo;
    }

    // En admin-inventario.js, modificar la función guardarProducto:
// En admin-inventario.js, modificar la función guardarProducto:
async guardarProducto() {
    const formData = {
        id: document.getElementById('producto-id').value || null,
        nombre: document.getElementById('producto-nombre').value.trim(),
        descripcion: document.getElementById('producto-descripcion').value.trim(),
        precio: parseFloat(document.getElementById('producto-precio').value),
        stock: parseInt(document.getElementById('producto-stock').value),
        categoria_id: parseInt(document.getElementById('producto-categoria').value),
        imagen: document.getElementById('producto-imagen').value.trim(),
        activo: document.getElementById('producto-activo').checked
    };

    // ✅ AUTO-DESHABILITAR SI STOCK ES 0
    if (formData.stock === 0) {
        formData.activo = false;
        console.log('🔴 Producto deshabilitado automáticamente por stock 0');
    }

    // Validaciones básicas
    if (!formData.nombre || formData.nombre === '') {
        this.mostrarNotificacion('El nombre del producto es requerido', 'error');
        return;
    }

    if (!formData.precio || formData.precio <= 0) {
        this.mostrarNotificacion('El precio debe ser mayor a 0', 'error');
        return;
    }

    if (formData.stock < 0) {
        this.mostrarNotificacion('El stock no puede ser negativo', 'error');
        return;
    }

    if (!formData.categoria_id) {
        this.mostrarNotificacion('Debe seleccionar una categoría', 'error');
        return;
    }

    try {
        // Resto del código igual...
        const url = formData.id ? '/api/admin/productos/editar' : '/api/admin/productos/agregar';
        const method = formData.id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            let mensaje = formData.id ? '✅ Producto actualizado correctamente' : '✅ Producto agregado correctamente';
            
            // ✅ AGREGAR INFORMACIÓN SOBRE ESTADO
            if (formData.stock === 0) {
                mensaje += ' (Producto deshabilitado por stock 0)';
            }
            
            this.mostrarNotificacion(mensaje, 'success');
            this.ocultarModal();
            await this.cargarProductos();
            this.notificarActualizacionProductos();
        } else {
            this.mostrarNotificacion(data.error, 'error');
        }
    } catch (error) {
        console.error('❌ Error guardando producto:', error);
        this.mostrarNotificacion('Error al guardar el producto', 'error');
    }
}

    // ✅ NUEVO MÉTODO: Notificar actualización de productos
    notificarActualizacionProductos() {
        // Disparar evento personalizado para que las vistas se actualicen
        const event = new CustomEvent('productosActualizados');
        document.dispatchEvent(event);
        console.log('🔄 Evento de actualización de productos disparado');
    }

    async validarProductoExistente(nombre, categoriaId) {
        try {
            const response = await fetch(`/api/admin/productos/validar?nombre=${encodeURIComponent(nombre)}&categoria_id=${categoriaId}`);
            const data = await response.json();
            
            return data.existe;
        } catch (error) {
            console.error('❌ Error validando producto:', error);
            return false;
        }
    }

    async validarProductoDuplicado(productoId, nombre, categoriaId) {
        try {
            const response = await fetch(`/api/admin/productos/validar?nombre=${encodeURIComponent(nombre)}&categoria_id=${categoriaId}&excluir_id=${productoId}`);
            const data = await response.json();
            
            return data.existe;
        } catch (error) {
            console.error('❌ Error validando duplicado:', error);
            return false;
        }
    }

    async validarNombreEnTiempoReal() {
        const nombre = document.getElementById('producto-nombre').value.trim();
        const categoriaId = document.getElementById('producto-categoria').value;
        const productoId = document.getElementById('producto-id').value;
        
        if (!nombre || !categoriaId) {
            this.limpiarErrorCampo('producto-nombre');
            return;
        }
        
        try {
            let url = `/api/admin/productos/validar?nombre=${encodeURIComponent(nombre)}&categoria_id=${categoriaId}`;
            if (productoId) {
                url += `&excluir_id=${productoId}`;
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.existe) {
                this.mostrarErrorCampo('producto-nombre', 'Ya existe un producto con este nombre en la categoría seleccionada');
            } else {
                this.limpiarErrorCampo('producto-nombre');
            }
        } catch (error) {
            console.error('❌ Error en validación en tiempo real:', error);
        }
    }

    mostrarErrorCampo(campoId, mensaje) {
        const campo = document.getElementById(campoId);
        campo.style.borderColor = '#e74c3c';
        
        this.limpiarErrorCampo(campoId);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.color = '#e74c3c';
        errorDiv.style.fontSize = '12px';
        errorDiv.style.marginTop = '5px';
        errorDiv.textContent = mensaje;
        
        campo.parentNode.appendChild(errorDiv);
    }

    limpiarErrorCampo(campoId) {
        const campo = document.getElementById(campoId);
        campo.style.borderColor = '';
        
        const errorMsg = campo.parentNode.querySelector('.error-message');
        if (errorMsg) {
            errorMsg.remove();
        }
    }

    limpiarErroresFormulario() {
        this.limpiarErrorCampo('producto-nombre');
        this.limpiarErrorCampo('producto-precio');
        this.limpiarErrorCampo('producto-stock');
        this.limpiarErrorCampo('producto-categoria');
    }

    async editarProducto(id) {
        const producto = this.productos.find(p => p.id === id);
        if (producto) {
            this.mostrarModal(producto);
        }
    }

    async toggleEstado(id, nuevoEstado) {
        try {
            const response = await fetch('/api/admin/productos/estado', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: id,
                    activo: nuevoEstado
                })
            });

            const data = await response.json();

            if (data.success) {
                this.mostrarNotificacion(
                    nuevoEstado ? '✅ Producto activado correctamente' : '✅ Producto desactivado correctamente',
                    'success'
                );
                await this.cargarProductos();
                this.notificarActualizacionProductos();
            } else {
                this.mostrarNotificacion(data.error, 'error');
            }
        } catch (error) {
            console.error('❌ Error cambiando estado:', error);
            this.mostrarNotificacion('Error al cambiar el estado', 'error');
        }
    }

    async eliminarProducto(id) {
        if (!confirm('¿Estás seguro de que quieres eliminar este producto? Esta acción no se puede deshacer.')) {
            return;
        }

        try {
            const response = await fetch(`/api/admin/productos/eliminar/${id}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.mostrarNotificacion('✅ Producto eliminado correctamente', 'success');
                await this.cargarProductos();
                this.notificarActualizacionProductos();
            } else {
                this.mostrarNotificacion(data.error, 'error');
            }
        } catch (error) {
            console.error('❌ Error eliminando producto:', error);
            this.mostrarNotificacion('Error al eliminar el producto', 'error');
        }
    }

    mostrarNotificacion(mensaje, tipo) {
        const notificacion = document.createElement('div');
        notificacion.className = `notification-custom ${tipo}`;
        notificacion.innerHTML = `
            <div class="notification-content">
                <i class="fa-solid fa-${tipo === 'success' ? 'check' : 'exclamation'}"></i>
                <span>${mensaje}</span>
            </div>
        `;
        
        document.body.appendChild(notificacion);
        setTimeout(() => {
            if (notificacion.parentNode) {
                notificacion.parentNode.removeChild(notificacion);
            }
        }, 3000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.adminInventario = new AdminInventario();
});