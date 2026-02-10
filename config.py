import os
import re
from urllib.parse import urlparse

class Config:
    
    # PayPal Configuration
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', 'AYTSE0ArUGWvO29fpicACxOAmMPpVmlF30LzJg7dptoX6DDySJJ_CrFlnOdhqmcFT7modd8eTVydWZvb')
    PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', 'EMA2vOKqstAjAZSzTU7V_mFOywC0iePTzVGUFd07pExHKyGBm_pmYe159R1oOg2THCCxPf-LMHZ9gQni')
    PAYPAL_MODE = 'sandbox'
    
    # Mercado Pago Configuration
    # Set these in your environment: MERCADOPAGO_ACCESS_TOKEN and MERCADOPAGO_PUBLIC_KEY
    MERCADOPAGO_ACCESS_TOKEN = os.environ.get('MERCADOPAGO_ACCESS_TOKEN', '')
    MERCADOPAGO_PUBLIC_KEY = os.environ.get('MERCADOPAGO_PUBLIC_KEY', '')
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-super-secreta-para-flask'
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        raise ValueError("ERROR: Error de conexion con BD.")
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
        }
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}