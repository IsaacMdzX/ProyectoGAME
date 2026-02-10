// User menu functionality - ADMIN VERSION
document.addEventListener('DOMContentLoaded', function() {
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenuBtn && userDropdown) {
        userMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const isVisible = userDropdown.style.display === 'block';
            userDropdown.style.display = isVisible ? 'none' : 'block';
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function() {
            userDropdown.style.display = 'none';
        });

        // Prevent dropdown from closing when clicking inside
        userDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    // Menú móvil (barra lateral)
    const sidebar = document.querySelector('.barra_lateral');
    if (sidebar) {
        const menuButton = document.createElement('button');
        menuButton.className = 'menu-toggle-btn';
        menuButton.setAttribute('aria-label', 'Abrir menú');
        menuButton.innerHTML = '<i class="fa-solid fa-bars"></i>';

        const overlay = document.createElement('div');
        overlay.className = 'menu-overlay';

        document.body.appendChild(menuButton);
        document.body.appendChild(overlay);

        const openMenu = () => {
            sidebar.classList.add('open');
            overlay.classList.add('show');
            document.body.classList.add('menu-open');
            menuButton.setAttribute('aria-label', 'Cerrar menú');
        };

        const closeMenu = () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('show');
            document.body.classList.remove('menu-open');
            menuButton.setAttribute('aria-label', 'Abrir menú');
        };

        menuButton.addEventListener('click', () => {
            if (sidebar.classList.contains('open')) {
                closeMenu();
            } else {
                openMenu();
            }
        });

        overlay.addEventListener('click', closeMenu);

        sidebar.addEventListener('click', (event) => {
            if (window.innerWidth <= 768 && event.target.closest('a')) {
                closeMenu();
            }
        });

        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                closeMenu();
            }
        });
    }

    // Cargar información del usuario si está logueado
    cargarUsuarioActual();
});

async function cargarUsuarioActual() {
    try {
        const response = await fetch('/api/usuario/actual');
        if (response.ok) {
            const usuario = await response.json();
            if (usuario && usuario.id) {
                // Verificar si es administrador (role = 1)
                const esAdmin = usuario.role === 1;
                actualizarMenuUsuario(usuario, true, esAdmin);
            } else {
                actualizarMenuUsuario(null, false, false);
            }
        } else {
            actualizarMenuUsuario(null, false, false);
        }
    } catch (error) {
        console.error('Error al cargar usuario:', error);
        actualizarMenuUsuario(null, false, false);
    }
}

function actualizarMenuUsuario(usuario, estaLogueado, esAdmin) {
    const dropdownContent = document.querySelector('.dropdown-content');
    if (!dropdownContent) {
        console.error('No se encontró el elemento dropdown-content');
        return;
    }

    if (estaLogueado && usuario) {
        if (esAdmin) {
            // Menú para ADMINISTRADORES
            dropdownContent.innerHTML = `
                <a href="/admin/perfil" class="dropdown-item">
                    <i class="fa-solid fa-user-gear"></i>
                    <span>Perfil</span>
                </a>
                <div class="dropdown-divider"></div>
                <a href="/logout" class="dropdown-item">
                    <i class="fa-solid fa-right-from-bracket"></i>
                    <span>Cerrar Sesión</span>
                </a>
            `;
        } else {
            // Menú para USUARIOS NORMALES
            dropdownContent.innerHTML = `
                <a href="/perfil" class="dropdown-item">
                    <i class="fa-solid fa-user"></i>
                    <span>Mi Perfil</span>
                </a>
                <div class="dropdown-divider"></div>
                <a href="/logout" class="dropdown-item">
                    <i class="fa-solid fa-right-from-bracket"></i>
                    <span>Cerrar Sesión</span>
                </a>
            `;
        }
    } else {
        // Menú para usuarios NO logueados
        dropdownContent.innerHTML = `
            <a href="/login" class="dropdown-item">
                <i class="fa-solid fa-right-to-bracket"></i>
                <span>Iniciar Sesión</span>
            </a>
            <a href="/registro" class="dropdown-item">
                <i class="fa-solid fa-user-plus"></i>
                <span>Registrarse</span>
            </a>
        `;
    }
    
    // Asegurar que el dropdown esté oculto inicialmente
    const userDropdown = document.getElementById('userDropdown');
    if (userDropdown) {
        userDropdown.style.display = 'none';
    }
}