// Modelo de Usuario para Backbone
var Usuario = Backbone.Model.extend({
    defaults: {
        username: '',
        email: '',
        password: '',
        confirm_password: ''
    },
    
    url: '/api/registro',
    
    validate: function(attrs) {
        var errors = [];
        
        if (!attrs.username || attrs.username.length < 6) {
            errors.push('El nombre de usuario debe tener al menos 6 caracteres');
        }
        
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!attrs.email || !emailRegex.test(attrs.email)) {
            errors.push('Ingresa un email válido');
        }
        
        if (!attrs.password || attrs.password.length < 8) {
            errors.push('La contraseña debe tener al menos 8 caracteres');
        }
        
        if (attrs.password !== attrs.confirm_password) {
            errors.push('Las contraseñas no coinciden');
        }
        
        return errors.length > 0 ? errors : undefined;
    }
});

// Vista del Formulario de Registro
var RegistroView = Backbone.View.extend({
    el: '#registro-form',
    
    events: {
        'submit': 'registrarUsuario',
        'input #username': 'limpiarError',
        'input #email': 'limpiarError', 
        'input #password': 'limpiarError',
        'input #confirm-password': 'limpiarError'
    },
    
    initialize: function() {
        this.usuario = new Usuario();
        this.listenTo(this.usuario, 'invalid', this.mostrarErrores);
        this.listenTo(this.usuario, 'sync', this.registroExitoso);
        this.listenTo(this.usuario, 'error', this.registroFallido);
    },
    
    registrarUsuario: function(e) {
        e.preventDefault();
        
        var datos = {
            username: this.$('#username').val(),
            email: this.$('#email').val(),
            password: this.$('#password').val(),
            confirm_password: this.$('#confirm-password').val()
        };
        
        this.limpiarTodosErrores();
        this.usuario.set(datos);
        
        if (this.usuario.isValid()) {
            this.mostrarCargando(true);
            this.usuario.save();
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
        this.$('.register-btn').before($errorDiv);
        
        setTimeout(function() {
            $errorDiv.fadeOut(function() {
                $(this).remove();
            });
        }, 5000);
    },
    
    registroExitoso: function() {
        this.mostrarCargando(false);
        this.mostrarExito('¡Cuenta creada exitosamente! Redirigiendo...');
        
        setTimeout(function() {
            window.location.href = '/login';
        }, 2000);
    },
    
    registroFallido: function(model, response) {
        this.mostrarCargando(false);
        var mensaje = response.responseJSON && response.responseJSON.error 
                     ? response.responseJSON.error 
                     : 'Error en el servidor. Intenta nuevamente.';
        this.mostrarErrorGeneral(mensaje);
    },
    
    mostrarCargando: function(mostrar) {
        var $btn = this.$('#registro-btn');
        if (mostrar) {
            $btn.html('<i class="fa-solid fa-spinner fa-spin"></i> Creando cuenta...');
            $btn.prop('disabled', true);
        } else {
            $btn.html('<i class="fa-solid fa-user-plus"></i> Crear Cuenta');
            $btn.prop('disabled', false);
        }
    },
    
    mostrarExito: function(mensaje) {
        var $exitoDiv = $('<div class="exito-alerta">').text(mensaje);
        this.$('#registro-btn').before($exitoDiv);
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
    new RegistroView();
});