// JavaScript para la gestión de pedidos
        document.addEventListener('DOMContentLoaded', function() {
            let pedidos = [];
            let filtrosActuales = {};
            
            // Elementos DOM
            const searchInput = document.getElementById('searchInput');
            const searchButton = document.getElementById('searchButton');
            const filtroEstado = document.getElementById('filtroEstado');
            const filtroFechaInicio = document.getElementById('filtroFechaInicio');
            const filtroFechaFin = document.getElementById('filtroFechaFin');
            const btnLimpiarFiltros = document.getElementById('btnLimpiarFiltros');
            const tbodyPedidos = document.getElementById('tbodyPedidos');
            const contadorPedidos = document.getElementById('contadorPedidos');
            const loadingPedidos = document.getElementById('loadingPedidos');
            const tablaPedidosContainer = document.getElementById('tablaPedidosContainer');
            const noPedidos = document.getElementById('noPedidos');
            
            // Cargar pedidos al iniciar
            cargarPedidos();
            
            // Event listeners
            searchButton.addEventListener('click', aplicarFiltros);
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') aplicarFiltros();
            });
            
            filtroEstado.addEventListener('change', aplicarFiltros);
            filtroFechaInicio.addEventListener('change', aplicarFiltros);
            filtroFechaFin.addEventListener('change', aplicarFiltros);
            btnLimpiarFiltros.addEventListener('click', limpiarFiltros);
            
            function cargarPedidos(filtros = {}) {
                loadingPedidos.style.display = 'block';
                tablaPedidosContainer.style.display = 'none';
                noPedidos.style.display = 'none';
                
                // Construir URL con filtros
                let url = '/api/admin/pedidos?';
                const params = new URLSearchParams();
                
                if (filtros.search) params.append('search', filtros.search);
                if (filtros.estado) params.append('estado', filtros.estado);
                if (filtros.fecha_inicio) params.append('fecha_inicio', filtros.fecha_inicio);
                if (filtros.fecha_fin) params.append('fecha_fin', filtros.fecha_fin);
                
                fetch(url + params.toString())
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            pedidos = data.pedidos;
                            mostrarPedidos(pedidos);
                            actualizarContador(pedidos.length);
                        } else {
                            throw new Error(data.error || 'Error al cargar pedidos');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Error al cargar los pedidos: ' + error.message);
                    })
                    .finally(() => {
                        loadingPedidos.style.display = 'none';
                    });
            }
            
            function mostrarPedidos(pedidos) {
                tbodyPedidos.innerHTML = '';
                
                if (pedidos.length === 0) {
                    noPedidos.style.display = 'block';
                    tablaPedidosContainer.style.display = 'none';
                    return;
                }
                
                tablaPedidosContainer.style.display = 'block';
                noPedidos.style.display = 'none';
                
                pedidos.forEach(pedido => {
                    const fila = document.createElement('tr');
                    
                    // Obtener nombres de productos (máximo 2 para no hacer muy larga la celda)
                    const productosTexto = pedido.productos.slice(0, 2).map(p => 
                        `${p.producto_nombre} (${p.cantidad})`
                    ).join(', ');
                    
                    const productosExtra = pedido.productos.length > 2 ? 
                        ` y ${pedido.productos.length - 2} más...` : '';
                    
                    fila.innerHTML = `
                        <td>${pedido.numero_pedido}</td>
                        <td>
                            <strong>${pedido.cliente_nombre}</strong><br>
                            <small>${pedido.cliente_email}</small>
                        </td>
                        <td>${productosTexto}${productosExtra}</td>
                        <td>${pedido.cantidad_total}</td>
                        <td>$${pedido.total_pedido.toFixed(2)}</td>
                        <td>
                            <span class="status-badge ${pedido.estado}">
                                ${pedido.estado}
                            </span>
                        </td>
                        <td>${pedido.fecha_pedido}</td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn-icon ver-detalle" title="Ver detalle" data-pedido-id="${pedido.id_pedido}">
                                    <i class="fa-solid fa-eye"></i>
                                </button>
                                <button class="btn-icon editar-estado" title="Cambiar estado" data-pedido-id="${pedido.id_pedido}">
                                    <i class="fa-solid fa-edit"></i>
                                </button>
                            </div>
                        </td>
                    `;
                    
                    tbodyPedidos.appendChild(fila);
                });
                
                // Agregar event listeners a los botones
                document.querySelectorAll('.ver-detalle').forEach(btn => {
                    btn.addEventListener('click', function() {
                        const pedidoId = this.getAttribute('data-pedido-id');
                        verDetallePedido(pedidoId);
                    });
                });
                
                document.querySelectorAll('.editar-estado').forEach(btn => {
                    btn.addEventListener('click', function() {
                        const pedidoId = this.getAttribute('data-pedido-id');
                        cambiarEstadoPedido(pedidoId);
                    });
                });
            }
            
            function aplicarFiltros() {
                filtrosActuales = {
                    search: searchInput.value.trim(),
                    estado: filtroEstado.value,
                    fecha_inicio: filtroFechaInicio.value,
                    fecha_fin: filtroFechaFin.value
                };
                
                cargarPedidos(filtrosActuales);
            }
            
            function limpiarFiltros() {
                searchInput.value = '';
                filtroEstado.value = '';
                filtroFechaInicio.value = '';
                filtroFechaFin.value = '';
                
                filtrosActuales = {};
                cargarPedidos();
            }
            
            function actualizarContador(cantidad) {
                contadorPedidos.textContent = `${cantidad} pedido${cantidad !== 1 ? 's' : ''}`;
            }
            
            function verDetallePedido(pedidoId) {
                fetch(`/api/admin/pedidos/${pedidoId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            mostrarModalDetalle(data.pedido);
                        } else {
                            throw new Error(data.error || 'Error al cargar detalle');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Error al cargar el detalle del pedido: ' + error.message);
                    });
            }
            
            function mostrarModalDetalle(pedido) {
                const modal = document.getElementById('modalDetallePedido');
                const modalNumeroPedido = document.getElementById('modalNumeroPedido');
                const modalBody = document.getElementById('modalBodyDetalle');
                
                modalNumeroPedido.textContent = pedido.numero_pedido;
                
                let html = `
                    <div class="detail-section">
                        <h3 class="section-title">Información del Cliente</h3>
                        <div class="detail-info">
                            <p><strong>Nombre:</strong> ${pedido.cliente.nombre}</p>
                            <p><strong>Email:</strong> ${pedido.cliente.email}</p>
                            ${pedido.cliente.telefono ? `<p><strong>Teléfono:</strong> ${pedido.cliente.telefono}</p>` : ''}
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h3 class="section-title">Detalles del Pedido</h3>
                        <div class="detail-info">
                            <p><strong>Fecha:</strong> ${pedido.fecha_pedido}</p>
                            <p><strong>Estado:</strong> <span class="status-badge ${pedido.estado}">${pedido.estado}</span></p>
                            <p><strong>Dirección de envío:</strong> ${pedido.direccion_envio || 'No especificada'}</p>
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h3 class="section-title">Productos</h3>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Producto</th>
                                    <th>Cantidad</th>
                                    <th>Precio Unitario</th>
                                    <th>Total</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                
                pedido.items.forEach(item => {
                    html += `
                        <tr>
                            <td>${item.producto_nombre}</td>
                            <td>${item.cantidad}</td>
                            <td>$${item.precio_unitario.toFixed(2)}</td>
                            <td>$${item.total.toFixed(2)}</td>
                        </tr>
                    `;
                });
                
                html += `
                            </tbody>
                        </table>
                        <div class="totals-section">
                            <p><strong>Total del pedido:</strong> $${pedido.total.toFixed(2)}</p>
                        </div>
                    </div>
                `;
                
                modalBody.innerHTML = html;
                modal.style.display = 'block';
                
                // Cerrar modal
                modal.querySelector('.modal-close').addEventListener('click', () => {
                    modal.style.display = 'none';
                });
                
                window.addEventListener('click', (event) => {
                    if (event.target === modal) {
                        modal.style.display = 'none';
                    }
                });
            }
            
            function cambiarEstadoPedido(pedidoId) {
                const nuevoEstado = prompt('Ingresa el nuevo estado (pendiente, procesando, completado, cancelado):');
                
                if (!nuevoEstado) return;
                
                if (!['pendiente', 'procesando', 'completado', 'cancelado'].includes(nuevoEstado.toLowerCase())) {
                    alert('Estado no válido. Usa: pendiente, procesando, completado o cancelado');
                    return;
                }
                
                fetch('/api/admin/pedidos/estado', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        pedido_id: pedidoId,
                        estado: nuevoEstado.toLowerCase()
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        cargarPedidos(filtrosActuales); // Recargar con filtros actuales
                    } else {
                        throw new Error(data.error || 'Error al cambiar estado');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al cambiar estado: ' + error.message);
                });
            }
        });