// admin-usuarios.js
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const tablaUsuarios = document.getElementById('tabla-usuarios');
    const usuariosBody = document.getElementById('usuarios-body');
    const modalUsuario = document.getElementById('modal-usuario');
    const formUsuario = document.getElementById('form-usuario');
    const btnAgregarUsuario = document.getElementById('btn-agregar-usuario');
    const modalCerrar = document.getElementById('modal-cerrar');
    const btnGuardarUsuario = document.getElementById('btn-guardar-usuario');
    const modalTitulo = document.getElementById('modal-titulo');
    
    // Filtros
    const searchInput = document.getElementById('search-usuarios');
    const searchBtn = document.getElementById('search-btn-usuarios');
    const filtroRol = document.getElementById('filtro-rol');
    const filtroEstado = document.getElementById('filtro-estado');
    
    // Estadísticas
    const totalUsuarios = document.getElementById('total-usuarios');
    const usuariosActivos = document.getElementById('usuarios-activos');
    const usuariosInactivos = document.getElementById('usuarios-inactivos');
    const totalAdmins = document.getElementById('total-admins');

    let usuarios = [];
    let roles = [];
    let usuarioEditando = null;

    // Inicializar
    inicializar();

    async function inicializar() {
        await cargarRoles();
        await cargarUsuarios();
        configurarEventListeners();
    }

    function configurarEventListeners() {
        // Modal
        btnAgregarUsuario.addEventListener('click', () => abrirModal());
        modalCerrar.addEventListener('click', () => cerrarModal());
        
        // Formulario
        formUsuario.addEventListener('submit', guardarUsuario);
        
        // Filtros
        searchBtn.addEventListener('click', aplicarFiltros);
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') aplicarFiltros();
        });
        filtroRol.addEventListener('change', aplicarFiltros);
        filtroEstado.addEventListener('change', aplicarFiltros);
        
        // Cerrar modal al hacer clic fuera
        modalUsuario.addEventListener('click', (e) => {
            if (e.target === modalUsuario) cerrarModal();
        });
    }

    async function cargarRoles() {
        try {
            const response = await fetch('/api/admin/roles');
            const data = await response.json();
            
            if (data.success) {
                roles = data.roles;
                actualizarSelectRoles();
            } else {
                throw new Error(data.error || 'Error al cargar roles');
            }
        } catch (error) {
            console.error('Error cargando roles:', error);
            mostrarNotificacion('Error al cargar roles', 'error');
        }
    }

    function actualizarSelectRoles() {
        // Actualizar filtro de roles
        filtroRol.innerHTML = '<option value="">Todos los roles</option>';
    roles.forEach(rol => {
        filtroRol.innerHTML += `<option value="${rol.id_rol}">${rol.nombre}</option>`;
    });

        // Actualizar select del modal
        const selectRol = document.getElementById('usuario-rol');
    selectRol.innerHTML = '<option value="">Seleccionar rol</option>';
    roles.forEach(rol => {
        selectRol.innerHTML += `<option value="${rol.id_rol}">${rol.nombre}</option>`;
    });
    }

    async function cargarUsuarios() {
        try {
            const params = new URLSearchParams();
            const search = searchInput.value.trim();
            const rol = filtroRol.value;
            const estado = filtroEstado.value;

            if (search) params.append('search', search);
            if (rol) params.append('rol', rol);
            if (estado) params.append('estado', estado);

            const response = await fetch(`/api/admin/usuarios?${params}`);
            const data = await response.json();

            if (data.success) {
                usuarios = data.usuarios;
                renderizarUsuarios();
                actualizarEstadisticas();
            } else {
                throw new Error(data.error || 'Error al cargar usuarios');
            }
        } catch (error) {
            console.error('Error cargando usuarios:', error);
            mostrarNotificacion('Error al cargar usuarios', 'error');
        }
    }

    function renderizarUsuarios() {
        if (usuarios.length === 0) {
            usuariosBody.innerHTML = `
                <tr>
                    <td colspan="7" class="no-data">
                        <i class="fa-solid fa-users-slash"></i>
                        <p>No se encontraron usuarios</p>
                    </td>
                </tr>
            `;
            return;
        }

        usuariosBody.innerHTML = usuarios.map(usuario => `
            <tr>
                <td>${usuario.id}</td>
                <td>
                    <strong>${usuario.username}</strong>
                </td>
                <td>${usuario.email}</td>
                <td>${usuario.rol}</td>
                <td>
                    <span class="estado-badge ${usuario.activo ? 'activo' : 'inactivo'}">
                        ${usuario.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td>${formatearFecha(usuario.fecha_registro)}</td>
                <td>
                    <div class="producto-acciones">
                        <button class="btn-editar" onclick="editarUsuario(${usuario.id})">
                            <i class="fa-solid fa-edit"></i> Editar
                        </button>
                        ${usuario.activo ? 
                            `<button class="btn-desactivar" onclick="cambiarEstadoUsuario(${usuario.id}, false)">
                                <i class="fa-solid fa-user-slash"></i> Desactivar
                            </button>` :
                            `<button class="btn-activar" onclick="cambiarEstadoUsuario(${usuario.id}, true)">
                                <i class="fa-solid fa-user-check"></i> Activar
                            </button>`
                        }
                        <button class="btn-eliminar" onclick="eliminarUsuario(${usuario.id})">
                            <i class="fa-solid fa-trash"></i> Eliminar
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    function actualizarEstadisticas() {
        const total = usuarios.length;
        const activos = usuarios.filter(u => u.activo).length;
        const inactivos = total - activos;
        const admins = usuarios.filter(u => u.rol_id === 1).length;

        totalUsuarios.textContent = total;
        usuariosActivos.textContent = activos;
        usuariosInactivos.textContent = inactivos;
        totalAdmins.textContent = admins;
    }

    function abrirModal(usuario = null) {
        usuarioEditando = usuario;
        const esEdicion = usuario !== null;

        modalTitulo.textContent = esEdicion ? 'Editar Usuario' : 'Agregar Usuario';
        
        // Limpiar formulario
        formUsuario.reset();
        document.getElementById('usuario-id').value = '';
        
        // Configurar campos específicos para edición
        const passwordField = document.getElementById('usuario-password');
        const passwordLabel = document.getElementById('label-password');
        
        if (esEdicion) {
            // Llenar datos del usuario
            document.getElementById('usuario-id').value = usuario.id;
            document.getElementById('usuario-username').value = usuario.username;
            document.getElementById('usuario-email').value = usuario.email;
            document.getElementById('usuario-rol').value = usuario.rol_id;
            document.getElementById('usuario-activo').checked = usuario.activo;
            
            // Cambiar etiqueta de contraseña para edición
            passwordLabel.textContent = 'Nueva Contraseña (opcional)';
            passwordField.required = false;
        } else {
            passwordLabel.textContent = 'Contraseña';
            passwordField.required = true;
        }

        modalUsuario.style.display = 'block';
    }

    function cerrarModal() {
        modalUsuario.style.display = 'none';
        usuarioEditando = null;
        formUsuario.reset();
    }

    async function guardarUsuario(e) {
        e.preventDefault();
        
        const usuarioId = document.getElementById('usuario-id').value;
        const username = document.getElementById('usuario-username').value.trim();
        const email = document.getElementById('usuario-email').value.trim();
        const password = document.getElementById('usuario-password').value;
        const rolId = document.getElementById('usuario-rol').value;
        const activo = document.getElementById('usuario-activo').checked;

        // Validaciones básicas
        if (!username || !email || !rolId) {
            mostrarNotificacion('Por favor complete todos los campos requeridos', 'error');
            return;
        }

        if (!usuarioId && !password) {
            mostrarNotificacion('La contraseña es requerida para nuevos usuarios', 'error');
            return;
        }

        if (password && password.length < 8) {
            mostrarNotificacion('La contraseña debe tener al menos 8 caracteres', 'error');
            return;
        }

        const usuarioData = {
            username: username,
            email: email,
            rol_id: parseInt(rolId),
            activo: activo
        };

        // Solo incluir password si se proporciona (en edición)
        if (password) {
            usuarioData.password = password;
        }

        try {
            let response;
            if (usuarioId) {
                // Editar usuario existente
                usuarioData.id = parseInt(usuarioId);
                response = await fetch('/api/admin/usuarios/editar', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(usuarioData)
                });
            } else {
                // Crear nuevo usuario
                response = await fetch('/api/admin/usuarios/agregar', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(usuarioData)
                });
            }

            const data = await response.json();

            if (data.success) {
                mostrarNotificacion(data.message, 'success');
                cerrarModal();
                await cargarUsuarios();
            } else {
                throw new Error(data.error || 'Error al guardar usuario');
            }
        } catch (error) {
            console.error('Error guardando usuario:', error);
            mostrarNotificacion(error.message, 'error');
        }
    }

    // Funciones globales para los botones de acción
    window.editarUsuario = function(id) {
        const usuario = usuarios.find(u => u.id === id);
        if (usuario) {
            abrirModal(usuario);
        }
    };

    window.cambiarEstadoUsuario = async function(id, activo) {
        const usuario = usuarios.find(u => u.id === id);
        if (!usuario) return;

        const accion = activo ? 'activar' : 'desactivar';
        const confirmar = confirm(`¿Estás seguro de que quieres ${accion} al usuario ${usuario.username}?`);

        if (!confirmar) return;

        try {
            const response = await fetch('/api/admin/usuarios/editar', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: id,
                    activo: activo
                })
            });

            const data = await response.json();

            if (data.success) {
                mostrarNotificacion(data.message, 'success');
                await cargarUsuarios();
            } else {
                throw new Error(data.error || `Error al ${accion} usuario`);
            }
        } catch (error) {
            console.error(`Error ${accion} usuario:`, error);
            mostrarNotificacion(error.message, 'error');
        }
    };

    window.eliminarUsuario = async function(id) {
        const usuario = usuarios.find(u => u.id === id);
        if (!usuario) return;

        const confirmar = confirm(`¿Estás seguro de que quieres eliminar al usuario ${usuario.username}? Esta acción no se puede deshacer.`);

        if (!confirmar) return;

        try {
            const response = await fetch(`/api/admin/usuarios/eliminar/${id}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                mostrarNotificacion(data.message, 'success');
                await cargarUsuarios();
            } else {
                throw new Error(data.error || 'Error al eliminar usuario');
            }
        } catch (error) {
            console.error('Error eliminando usuario:', error);
            mostrarNotificacion(error.message, 'error');
        }
    };

    function aplicarFiltros() {
        cargarUsuarios();
    }

    function formatearFecha(fechaString) {
        if (!fechaString) return 'N/A';
        
        const fecha = new Date(fechaString);
        return fecha.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    }

    function mostrarNotificacion(mensaje, tipo) {
        // Crear notificación
        const notificacion = document.createElement('div');
        notificacion.className = `notification-custom ${tipo}`;
        notificacion.innerHTML = `
            <div class="notification-content">
                <i class="fa-solid ${tipo === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span>${mensaje}</span>
            </div>
        `;

        document.body.appendChild(notificacion);

        // Remover después de 5 segundos
        setTimeout(() => {
            notificacion.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                if (notificacion.parentNode) {
                    notificacion.parentNode.removeChild(notificacion);
                }
            }, 300);
        }, 5000);
    }
});