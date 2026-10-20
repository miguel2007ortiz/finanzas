from django.contrib import admin
from .models import *

# Registramos los modelos para que aparezcan en el panel visual
admin.site.register(CuentaFija)
admin.site.register(Categoria)
admin.site.register(GastoMensual)
admin.site.register(IngresoMensual)