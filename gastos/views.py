from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from decimal import Decimal
from datetime import datetime, date
from calendar import monthrange
from .models import *
from .forms import *
import json


def procesar_gastos_recurrentes_hoy():
    hoy = date.today()

    for gasto_recurrente in GastoRecurrente.objects.filter(activo=True):
        if gasto_recurrente.ultimo_proceso and gasto_recurrente.ultimo_proceso.year == hoy.year and gasto_recurrente.ultimo_proceso.month == hoy.month:
            continue

        ultimo_dia_mes = monthrange(hoy.year, hoy.month)[1]
        dia = min(int(gasto_recurrente.dia_mes), ultimo_dia_mes)
        fecha_gasto = date(hoy.year, hoy.month, dia)

        gasto_existente = GastoMensual.objects.filter(
            usuario=gasto_recurrente.usuario,
            concepto=gasto_recurrente.concepto,
            categoria=gasto_recurrente.categoria,
            cuenta=gasto_recurrente.cuenta,
            monto=gasto_recurrente.monto,
            fecha=fecha_gasto,
        ).exists()

        if gasto_existente:
            gasto_recurrente.ultimo_proceso = date(hoy.year, hoy.month, 1)
            gasto_recurrente.save(update_fields=['ultimo_proceso'])
            continue

        try:
            GastoMensual.objects.create(
                usuario=gasto_recurrente.usuario,
                concepto=gasto_recurrente.concepto,
                monto=gasto_recurrente.monto,
                categoria=gasto_recurrente.categoria,
                cuenta=gasto_recurrente.cuenta,
                fecha=fecha_gasto,
            )
            gasto_recurrente.ultimo_proceso = date(hoy.year, hoy.month, 1)
            gasto_recurrente.save(update_fields=['ultimo_proceso'])
        except ValidationError:
            continue


def historial_completo(request):
    hoy = datetime.now()
    mes_filtro = int(request.GET.get('mes_filtro', request.GET.get('mes', hoy.month)))
    anio_filtro = int(request.GET.get('anio_filtro', request.GET.get('anio', hoy.year)))

    gastos = GastoMensual.objects.filter(
        fecha__month=mes_filtro,
        fecha__year=anio_filtro,
    ).select_related('categoria', 'cuenta').order_by('-fecha', '-id')

    filtro_busqueda = request.GET.get('q', '').strip()
    monto_min = request.GET.get('monto_min', '').strip()
    monto_max = request.GET.get('monto_max', '').strip()

    if filtro_busqueda:
        gastos = gastos.filter(
            Q(concepto__icontains=filtro_busqueda) |
            Q(categoria__nombre__icontains=filtro_busqueda) |
            Q(cuenta__nombre__icontains=filtro_busqueda)
        )
    if monto_min:
        gastos = gastos.filter(monto__gte=Decimal(monto_min))
    if monto_max:
        gastos = gastos.filter(monto__lte=Decimal(monto_max))

    paginator = Paginator(gastos, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    meses_lista = [
        {'numero': 1, 'nombre': 'Enero'}, {'numero': 2, 'nombre': 'Febrero'},
        {'numero': 3, 'nombre': 'Marzo'}, {'numero': 4, 'nombre': 'Abril'},
        {'numero': 5, 'nombre': 'Mayo'}, {'numero': 6, 'nombre': 'Junio'},
        {'numero': 7, 'nombre': 'Julio'}, {'numero': 8, 'nombre': 'Agosto'},
        {'numero': 9, 'nombre': 'Septiembre'}, {'numero': 10, 'nombre': 'Octubre'},
        {'numero': 11, 'nombre': 'Noviembre'}, {'numero': 12, 'nombre': 'Diciembre'},
    ]
    anios_lista = range(hoy.year - 2, hoy.year + 2)

    total_gastos = gastos.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

    context = {
        'gastos': page_obj.object_list,
        'page_obj': page_obj,
        'mes_filtro': mes_filtro,
        'anio_filtro': anio_filtro,
        'meses_lista': meses_lista,
        'anios_lista': anios_lista,
        'q': filtro_busqueda,
        'monto_min': monto_min,
        'monto_max': monto_max,
        'total_gastos': total_gastos,
    }

    return render(request, 'gastos/historial_completo.html', context)


def resumen_finanzas(request):
    procesar_gastos_recurrentes_hoy()
    form_gasto = GastoForm()
    form_ingreso = IngresoForm()
    form_cuenta = CuentaFijaForm()
    form_meta = MetaAhorroForm()

    if request.method == 'POST':
        if 'action_gasto' in request.POST:
            form_gasto = GastoForm(request.POST)
            if form_gasto.is_valid():
                gasto = form_gasto.save(commit=False)
                gasto.usuario = User.objects.first()
                try:
                    gasto.save()
                    return redirect('resumen')
                except ValidationError as e:
                    form_gasto.add_error(None, e)

        elif 'action_ingreso' in request.POST:
            form_ingreso = IngresoForm(request.POST)
            if form_ingreso.is_valid():
                ingreso = form_ingreso.save(commit=False)
                ingreso.usuario = User.objects.first()
                ingreso.save()
                return redirect('resumen')

        elif 'action_cuenta' in request.POST:
            form_cuenta = CuentaFijaForm(request.POST)
            if form_cuenta.is_valid():
                cuenta = form_cuenta.save(commit=False)
                cuenta.usuario = User.objects.first()
                cuenta.save()
                return redirect('resumen')

        elif 'action_meta' in request.POST:
            form_meta = MetaAhorroForm(request.POST)
            if form_meta.is_valid():
                meta = form_meta.save(commit=False)
                meta.usuario = User.objects.first()
                meta.save()
                return redirect('resumen')

        elif 'action_editar_cuenta' in request.POST:
            cuenta_id = request.POST.get('cuenta_id')
            cuenta = CuentaFija.objects.filter(id=cuenta_id).first()
            if cuenta:
                form_editar = CuentaFijaForm(request.POST, instance=cuenta)
                if form_editar.is_valid():
                    form_editar.save()
                    return redirect('resumen')

        elif 'action_eliminar_cuenta' in request.POST:
            cuenta_id = request.POST.get('cuenta_id')
            cuenta = CuentaFija.objects.filter(id=cuenta_id).first()
            if cuenta:
                cuenta.delete()
                return redirect('resumen')

        elif 'action_editar_meta' in request.POST:
            meta_id = request.POST.get('meta_id')
            meta = MetaAhorro.objects.filter(id=meta_id).first()
            if meta:
                form_editar_meta = MetaAhorroForm(request.POST, instance=meta)
                if form_editar_meta.is_valid():
                    form_editar_meta.save()
                    return redirect('resumen')

        elif 'action_eliminar_meta' in request.POST:
            meta_id = request.POST.get('meta_id')
            meta = MetaAhorro.objects.filter(id=meta_id).first()
            if meta:
                meta.delete()
                return redirect('resumen')

        elif 'action_transferir_meta' in request.POST:
            cuenta_id = request.POST.get('cuenta_origen')
            meta_id = request.POST.get('meta_id')
            monto = Decimal(request.POST.get('monto_transferir', 0))

            cuenta = CuentaFija.objects.filter(id=cuenta_id).first()
            meta = MetaAhorro.objects.filter(id=meta_id).first()

            if cuenta and meta and monto > 0:
                if cuenta.saldo_actual >= monto:
                    cuenta.saldo_actual -= monto
                    cuenta.save()
                    meta.monto_actual += monto
                    meta.save()
                    return redirect('resumen')

    hoy = datetime.now()
    mes_filtro = int(request.GET.get('mes_filtro', request.GET.get('mes', hoy.month)))
    anio_filtro = int(request.GET.get('anio_filtro', request.GET.get('anio', hoy.year)))

    ingresos_filtrados = IngresoMensual.objects.filter(fecha__month=mes_filtro, fecha__year=anio_filtro)
    gastos_filtrados = GastoMensual.objects.filter(fecha__month=mes_filtro, fecha__year=anio_filtro)

    total_ingresos = ingresos_filtrados.aggregate(total=Sum('monto'))['total'] or 0
    total_gastos = gastos_filtrados.aggregate(total=Sum('monto'))['total'] or 0
    saldo_neto = total_ingresos - total_gastos

    mis_cuentas = CuentaFija.objects.all()
    metas_ahorro = MetaAhorro.objects.filter(usuario=User.objects.first())

    filtro_busqueda = request.GET.get('q', '').strip()
    monto_min = request.GET.get('monto_min', '').strip()
    monto_max = request.GET.get('monto_max', '').strip()

    historial_gastos = gastos_filtrados.select_related('categoria', 'cuenta').order_by('-fecha', '-id')
    if filtro_busqueda:
        historial_gastos = historial_gastos.filter(
            Q(concepto__icontains=filtro_busqueda) |
            Q(categoria__nombre__icontains=filtro_busqueda)
        )
    if monto_min:
        historial_gastos = historial_gastos.filter(monto__gte=Decimal(monto_min))
    if monto_max:
        historial_gastos = historial_gastos.filter(monto__lte=Decimal(monto_max))

    paginator = Paginator(historial_gastos, 6)
    pagina_numero = request.GET.get('page', 1)
    page_obj = paginator.get_page(pagina_numero)

    gastos_por_categoria = (
        gastos_filtrados.values('categoria__nombre', 'categoria__id')
        .annotate(total=Sum('monto'))
        .order_by('-total')
    )

    labels_grafico = [item['categoria__nombre'] for item in gastos_por_categoria]
    data_grafico = [float(item['total']) for item in gastos_por_categoria]

    categorias = Categoria.objects.filter(usuario=User.objects.first()).order_by('nombre')
    categorias_con_presupuesto = []

    for categoria in categorias:
        total_categoria = GastoMensual.objects.filter(
            categoria=categoria,
            fecha__month=mes_filtro,
            fecha__year=anio_filtro,
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

        limite = categoria.limite_mensual or Decimal('0.00')
        porcentaje = 0

        if limite > 0:
            porcentaje = min((float(total_categoria) / float(limite)) * 100, 100)

        estado = 'normal'
        if limite > 0 and total_categoria >= limite:
            estado = 'excedido'
        elif limite > 0 and total_categoria >= (limite * Decimal('0.8')):
            estado = 'alerta'

        categorias_con_presupuesto.append({
            'nombre': categoria.nombre,
            'limite': limite,
            'gastado': total_categoria,
            'porcentaje': porcentaje,
            'estado': estado,
        })

    meses_lista = [
        {'numero': 1, 'nombre': 'Enero'}, {'numero': 2, 'nombre': 'Febrero'},
        {'numero': 3, 'nombre': 'Marzo'}, {'numero': 4, 'nombre': 'Abril'},
        {'numero': 5, 'nombre': 'Mayo'}, {'numero': 6, 'nombre': 'Junio'},
        {'numero': 7, 'nombre': 'Julio'}, {'numero': 8, 'nombre': 'Agosto'},
        {'numero': 9, 'nombre': 'Septiembre'}, {'numero': 10, 'nombre': 'Octubre'},
        {'numero': 11, 'nombre': 'Noviembre'}, {'numero': 12, 'nombre': 'Diciembre'},
    ]

    anios_lista = range(hoy.year - 2, hoy.year + 2)

    context = {
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
        'saldo_neto': saldo_neto,
        'mis_cuentas': mis_cuentas,
        'ultimos_gastos': page_obj.object_list,
        'page_obj': page_obj,
        'form_gasto': form_gasto,
        'form_ingreso': form_ingreso,
        'form_cuenta': form_cuenta,
        'form_meta': form_meta,
        'metas_ahorro': metas_ahorro,
        'labels_grafico': json.dumps(labels_grafico),
        'data_grafico': json.dumps(data_grafico),
        'mes_filtro': mes_filtro,
        'anio_filtro': anio_filtro,
        'meses_lista': meses_lista,
        'anios_lista': anios_lista,
        'categorias_con_presupuesto': categorias_con_presupuesto,
        'q': filtro_busqueda,
        'monto_min': monto_min,
        'monto_max': monto_max,
    }

    return render(request, 'gastos/resumen.html', context)
