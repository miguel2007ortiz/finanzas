from django.db import migrations

def crear_categorias_defecto(apps, schema_editor):
    # Obtenemos el modelo Categoria de forma segura para migraciones
    Categoria = apps.get_model('gastos', 'Categoria')
    
    # Lista de categorías iniciales para organizar tus gastos mensuales
    categorias_iniciales = [
        {"nombre": "Arriendo / Vivienda", "descripcion": "Pago mensual de alquiler, hipoteca o gastos comunes"},
        {"nombre": "Servicios Públicos", "descripcion": "Luz, agua, gas, internet o telefonía"},
        {"nombre": "Alimentación", "descripcion": "Mercado mensual, compras de comida o restaurantes"},
        {"nombre": "Transporte", "descripcion": "Gasolina, pasajes de bus/metro, Uber o mantenimiento del vehículo"},
        {"nombre": "Salud y Bienestar", "descripcion": "Medicamentos, citas médicas o gimnasio"},
        {"nombre": "Suscripciones / Ocio", "descripcion": "Netflix, Spotify, salidas con amigos, etc."},
    ]

    for cat in categorias_iniciales:
        # get_or_create evita duplicarlas si vuelves a correr la migración
        Categoria.objects.get_or_create(nombre=cat["nombre"], defaults={"descripcion": cat["descripcion"]})

class Migration(migrations.Migration):

    dependencies = [
        ('gastos', '0001_initial'), # Revisa que coincida con el nombre de tu primera migración
    ]

    operations = [
        migrations.RunPython(crear_categorias_defecto),
    ]
