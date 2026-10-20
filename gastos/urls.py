from django.urls import path
from . import views

urlpatterns = [
    path('', views.resumen_finanzas, name='resumen'),
    path('historial-completo/', views.historial_completo, name='historial_completo'),
]