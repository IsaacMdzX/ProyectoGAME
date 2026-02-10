$(document).ready(function() {
    console.log('registro-admin.js cargado correctamente');

    // Función para mostrar errores
    function mostrarError(campo, mensaje) {
        $('#' + campo + '-error').text(mensaje).show();
    }

    // Función para limpiar errores
    function limpiarErrores() {
        $('.error-message').text('').hide();
        $('.error-alerta').remove();
    }

    // Función para validar email
    function validarEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    // Función para mostrar alerta de error
    function mostrarErrorGeneral(mensaje) {
        var $errorDiv = $('<div class="error-alerta" style="background: #ffebee; color: #c62828; padding: 10px; border-radius: 5px; margin: 10px 0; border: 1px solid #ffcdd2;">').text(mensaje);
        $('.register-btn').before($errorDiv);
        
        setTimeout(function() {
            $errorDiv.fadeOut(function() {
                $(this).remove();
            });
        }, 5000);
    }

    // Función para mostrar alerta de éxito
    function mostrarExito(mensaje) {
        var $exitoDiv = $('<div class="exito-alerta" style="background: #e8f5e8; color: #2e7d32; padding: 10px; border-radius: 5px; margin: 10px 0; border: 1px solid #c8e6c9;">').text(mensaje);
        $('.register-btn').before($exitoDiv);
    }

    // Función para mostrar/ocultar loading
    function mostrarCargando(mostrar) {
        var $btn = $('#registro-btn');
        if (mostrar) {
            $btn.html('<i class="fa-solid fa-spinner fa-spin"></i> Creando administrador...');
            $btn.prop('disabled', true);
        } else {
            $btn.html('<i class="fa-solid fa-shield-alt"></i> Crear Cuenta de Admin');
            $btn.prop('disabled', false);
        }
    }

    // Validación en tiempo real
    $('#username').on('input', function() {
        const username = $(this).val();
        if (username.length > 0 && username.length < 6) {
            mostrarError('username', 'El usuario debe tener al menos 6 caracteres');
        } else {
            $('#username-error').text('').hide();
        }
    });

    $('#email').on('input', function() {
        const email = $(this).val();
        if (email.length > 0 && !validarEmail(email)) {
            mostrarError('email', 'Email inválido');
        } else {
            $('#email-error').text('').hide();
        }
    });

    $('#password').on('input', function() {
        const password = $(this).val();
        if (password.length > 0 && password.length < 8) {
            mostrarError('password', 'La contraseña debe tener al menos 8 caracteres');
        } else {
            $('#password-error').text('').hide();
        }
    });

    $('#confirm-password').on('input', function() {
        const password = $('#password').val();
        const confirmPassword = $(this).val();
        if (confirmPassword.length > 0 && password !== confirmPassword) {
            mostrarError('confirm', 'Las contraseñas no coinciden');
        } else {
            $('#confirm-error').text('').hide();
        }
    });

    // Limpiar errores al hacer focus
    $('input').on('focus', function() {
        const fieldName = $(this).attr('id');
        $('#' + fieldName + '-error').text('').hide();
    });

    // Manejar envío del formulario
    $('#registro-form').on('submit', function(e) {
        e.preventDefault();
        console.log('Formulario enviado');
        
        limpiarErrores();

        const username = $('#username').val().trim();
        const email = $('#email').val().trim();
        const password = $('#password').val();
        const confirmPassword = $('#confirm-password').val();

        let hayErrores = false;

        // Validaciones
        if (!username) {
            mostrarError('username', 'El nombre de usuario es requerido');
            hayErrores = true;
        } else if (username.length < 6) {
            mostrarError('username', 'El usuario debe tener al menos 6 caracteres');
            hayErrores = true;
        }

        if (!email) {
            mostrarError('email', 'El email es requerido');
            hayErrores = true;
        } else if (!validarEmail(email)) {
            mostrarError('email', 'Email inválido');
            hayErrores = true;
        }

        if (!password) {
            mostrarError('password', 'La contraseña es requerida');
            hayErrores = true;
        } else if (password.length < 8) {
            mostrarError('password', 'La contraseña debe tener al menos 8 caracteres');
            hayErrores = true;
        }

        if (!confirmPassword) {
            mostrarError('confirm', 'Confirma tu contraseña');
            hayErrores = true;
        } else if (password !== confirmPassword) {
            mostrarError('confirm', 'Las contraseñas no coinciden');
            hayErrores = true;
        }

        if (hayErrores) {
            console.log('Errores de validación encontrados');
            return;
        }

        // Mostrar loading
        mostrarCargando(true);
        console.log('Enviando datos de administrador:', { username, email });

        // Enviar a la ruta CORRECTA para admin
        $.ajax({
            url: '/api/registro-admin',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                username: username,
                email: email,
                password: password,
                confirm_password: confirmPassword
            }),
            success: function(response) {
                console.log('Respuesta del servidor:', response);
                
                if (response.success) {
                    mostrarExito('¡Administrador creado exitosamente! Redirigiendo...');
                    
                    setTimeout(function() {
                        window.location.href = '/login';
                    }, 2000);
                    
                } else {
                    if (response.error) {
                        mostrarErrorGeneral(response.error);
                    }
                    mostrarCargando(false);
                }
            },
            error: function(xhr) {
                console.log('Error en AJAX:', xhr);
                
                let errorMessage = 'Error del servidor';
                
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                } else if (xhr.status === 0) {
                    errorMessage = 'No se pudo conectar al servidor';
                } else if (xhr.status === 500) {
                    errorMessage = 'Error interno del servidor';
                }
                
                mostrarErrorGeneral(errorMessage);
                mostrarCargando(false);
            }
        });
    });

    console.log('Eventos de registro-admin.js configurados');
});