// Modelo de Login para Backbone
var Login = Backbone.Model.extend({
    defaults: {
        login_input: '',
        password: ''
    },
    
    url: '/api/login',
    
    validate: function(attrs) {
        var errors = [];
        
        if (!attrs.login_input) {
            errors.push('Ingresa tu usuario o email');
        }
        
        if (!attrs.password) {
            errors.push('Ingresa tu contraseña');
        }
        
        return errors.length > 0 ? errors : undefined;
    }
});

// Vista del Formulario de Login
var LoginView = Backbone.View.extend({
    el: '#login-form',
    
    events: {
        'submit': 'iniciarSesion',
        'input #login-input': 'limpiarError',
        'input #login-password': 'limpiarError'
    },
    
    initialize: function() {
        this.login = new Login();
        this.listenTo(this.login, 'invalid', this.mostrarErrores);
        this.listenTo(this.login, 'sync', this.loginExitoso);
        this.listenTo(this.login, 'error', this.loginFallido);
    },
    
    iniciarSesion: function(e) {
        e.preventDefault();
        
        var datos = {
            login_input: this.$('#login-input').val(),
            password: this.$('#login-password').val()
        };
        
        this.limpiarTodosErrores();
        this.login.set(datos);
        
        if (this.login.isValid()) {
            this.mostrarCargando(true);
            this.login.save();
        }
    },
    
    mostrarErrores: function(model, errors) {
        this.mostrarCargando(false);
        errors.forEach(function(error) {
            this.mostrarErrorGeneral(error);
        }.bind(this));
    },
    
    mostrarErrorGeneral: function(mensaje) {
        var $errorDiv = $('<div class="error-alerta">').text(mensaje);
        this.$('#login-btn').before($errorDiv);
        
        setTimeout(function() {
            $errorDiv.fadeOut(function() {
                $(this).remove();
            });
        }, 5000);
    },
    
    loginExitoso: function(model, response) {
        this.mostrarCargando(false);
        this.mostrarExito('¡Sesión iniciada! Redirigiendo...');

        if (window.userMenu) {
        window.userMenu.updateMenu();
    }
        
        setTimeout(function() {
            // Redirigir a la página principal o perfil
            window.location.href = response.redirect_url || '/';
        }, 1500);
    },
    
    loginFallido: function(model, response) {
        this.mostrarCargando(false);
        var mensaje = response.responseJSON && response.responseJSON.error 
                     ? response.responseJSON.error 
                     : 'Error en el servidor. Intenta nuevamente.';
        this.mostrarErrorGeneral(mensaje);
    },
    
    mostrarCargando: function(mostrar) {
        var $btn = this.$('#login-btn');
        if (mostrar) {
            $btn.html('<i class="fa-solid fa-spinner fa-spin"></i> Iniciando sesión...');
            $btn.prop('disabled', true);
        } else {
            $btn.html('<i class="fa-solid fa-right-to-bracket"></i> Iniciar Sesión');
            $btn.prop('disabled', false);
        }
    },
    
    mostrarExito: function(mensaje) {
        var $exitoDiv = $('<div class="exito-alerta">').text(mensaje);
        this.$('#login-btn').before($exitoDiv);
    },
    
    limpiarError: function(e) {
        var $input = $(e.target);
        $input.removeClass('error-input');
        $input.siblings('.error-message').text('');
    },
    
    limpiarTodosErrores: function() {
        this.$('.error-alerta').remove();
        this.$('.error-input').removeClass('error-input');
        this.$('.error-message').text('');
    }
});

// Inicializar cuando el DOM esté listo
$(document).ready(function() {
    new LoginView();
});