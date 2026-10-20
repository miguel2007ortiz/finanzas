from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class CuentaFija(models.Model):
    """Representa cuentas de ahorro o dinero guardado"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cuentas')
    nombre = models.CharField(max_length=100)
    saldo_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - ${self.saldo_actual}"


class Categoria(models.Model):
    """Categorías para organizar los gastos (Arriendo, Servicios, etc.)"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    limite_mensual = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)

    def __str__(self):
        return self.nombre


class MetaAhorro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metas_ahorro')
    nombre = models.CharField(max_length=150)
    monto_objetivo = models.DecimalField(max_digits=12, decimal_places=2)
    monto_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    fecha_limite = models.DateField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def porcentaje_completado(self):
        if self.monto_objetivo <= 0:
            return 0
        return min((float(self.monto_actual) / float(self.monto_objetivo)) * 100, 100)

    def __str__(self):
        return f"{self.nombre} - ${self.monto_actual} / ${self.monto_objetivo}"


class GastoRecurrente(models.Model):
    """Gastos que se repiten cada mes."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gastos_recurrentes')
    concepto = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='gastos_recurrentes')
    cuenta = models.ForeignKey(CuentaFija, on_delete=models.SET_NULL, null=True, blank=True, related_name='gastos_recurrentes')
    dia_mes = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        default=1,
        help_text='Día del mes en que se cobrará el gasto.'
    )
    activo = models.BooleanField(default=True)
    fecha_inicio = models.DateField(auto_now_add=True)
    ultimo_proceso = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['dia_mes', 'concepto']

    def __str__(self):
        return f"{self.concepto} - ${self.monto} ({self.dia_mes})"


class GastoMensual(models.Model):
    """Apuntes de gastos mensuales que hace el usuario"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gastos')
    cuenta = models.ForeignKey(CuentaFija, on_delete=models.SET_NULL, null=True, blank=True, related_name='gastos')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='gastos')
    concepto = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    creado_en = models.DateTimeField(auto_now_add=True)
    alerta_presupuesto = models.BooleanField(default=False)
    supero_limite = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Gastos Mensuales"
        ordering = ['-fecha']

    def save(self, *args, **kwargs):
        if self.cuenta:
            if self.cuenta.saldo_actual < self.monto:
                raise ValidationError(f"Saldo insuficiente en {self.cuenta.nombre}. Saldo actual: ${self.cuenta.saldo_actual}")
            self.cuenta.saldo_actual -= self.monto
            self.cuenta.save()

        if self.categoria and self.categoria.limite_mensual:
            total_mes = GastoMensual.objects.filter(
                categoria=self.categoria,
                fecha__month=self.fecha.month,
                fecha__year=self.fecha.year,
            ).exclude(pk=self.pk).aggregate(total=models.Sum('monto'))['total'] or 0

            total_total = total_mes + self.monto

            if total_total > self.categoria.limite_mensual:
                self.alerta_presupuesto = True
                self.supero_limite = True
            else:
                self.alerta_presupuesto = total_total >= (self.categoria.limite_mensual * 0.8)
                self.supero_limite = False
        else:
            self.alerta_presupuesto = False
            self.supero_limite = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fecha.strftime('%B %Y')} - {self.concepto}: ${self.monto}"


class IngresoMensual(models.Model):
    """Representa los ingresos mensuales del usuario (Sueldo, Ventas, etc.)"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ingresos')
    cuenta = models.ForeignKey(CuentaFija, on_delete=models.SET_NULL, null=True, blank=True, related_name='ingresos')
    concepto = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Ingresos Mensuales"
        ordering = ['-fecha']

    def save(self, *args, **kwargs):
        if self.cuenta:
            self.cuenta.saldo_actual += self.monto
            self.cuenta.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ingreso: {self.concepto} - ${self.monto}"

