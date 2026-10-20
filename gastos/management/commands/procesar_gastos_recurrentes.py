from datetime import date
from calendar import monthrange
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from gastos.models import GastoRecurrente, GastoMensual


class Command(BaseCommand):
    help = 'Genera automáticamente los gastos recurrentes activos del mes actual.'

    def handle(self, *args, **options):
        hoy = date.today()
        creados = 0

        for gasto_recurrente in GastoRecurrente.objects.filter(activo=True):
            if gasto_recurrente.ultimo_proceso and gasto_recurrente.ultimo_proceso.year == hoy.year and gasto_recurrente.ultimo_proceso.month == hoy.month:
                continue

            ultimo_dia_mes = monthrange(hoy.year, hoy.month)[1]
            dia = min(int(gasto_recurrente.dia_mes), ultimo_dia_mes)
            fecha_gasto = date(hoy.year, hoy.month, dia)

            ya_existe = GastoMensual.objects.filter(
                usuario=gasto_recurrente.usuario,
                concepto=gasto_recurrente.concepto,
                categoria=gasto_recurrente.categoria,
                cuenta=gasto_recurrente.cuenta,
                monto=gasto_recurrente.monto,
                fecha=fecha_gasto,
            ).exists()

            if ya_existe:
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
                creados += 1
            except ValidationError:
                self.stdout.write(
                    self.style.WARNING(
                        f'Se omitió {gasto_recurrente.concepto} porque la cuenta no tiene saldo suficiente.'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f'Gastos recurrentes procesados: {creados}')
        )
