# WSGI entry point para Render/Gunicorn
# Render ejecuta este módulo desde el directorio del backend.
# La ruta será la ubicación real de este archivo dentro del checkout de Git.

import sys, os

# Añadir el directorio del backend al path sin depender del nombre de usuario.
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Importar la app Flask desde app.py
from app import app as application

# Gunicorn usa 'application' como objeto WSGI.
