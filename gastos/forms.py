from django import forms
from .models import *


class MetaAhorroForm(forms.ModelForm):
    class Meta:
        model = MetaAhorro
        fields = ['nombre', 'monto_objetivo', 'monto_actual', 'fecha_limite']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none bg-white text-slate-900',
                'placeholder': 'Ej. Moto, Viaje, Emergencias'
            }),
            'monto_objetivo': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none bg-white text-slate-900',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'monto_actual': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none bg-white text-slate-900',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'fecha_limite': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none bg-white text-slate-900',
                'type': 'date'
            }),
        }


class GastoForm(forms.ModelForm):
    class Meta:
        model = GastoMensual
        # Excluimos al usuario por ahora, lo asignaremos automáticamente en la vista
        fields = ['concepto', 'monto', 'categoria', 'cuenta', 'fecha']
        
        # Añadimos widgets para que Tailwind les dé un diseño moderno
        widgets = {
            'concepto': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-hidden bg-white text-slate-900',
                'placeholder': 'Ej. Pago de arriendo del mes'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-hidden bg-white text-slate-900',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'categoria': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-hidden bg-white text-slate-900'
            }),
            'cuenta': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-hidden bg-white text-slate-900'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-hidden bg-white text-slate-900',
                'type': 'date'
            }),
        }


class IngresoForm(forms.ModelForm):
    class Meta:
        model = IngresoMensual
        fields = ['concepto', 'monto', 'cuenta', 'fecha']
        
        widgets = {
            'concepto': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-hidden bg-white text-slate-900',
                'placeholder': 'Ej. Sueldo quincenal o Venta online'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-hidden bg-white text-slate-900',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'cuenta': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-hidden bg-white text-slate-900'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-hidden bg-white text-slate-900',
                'type': 'date'
            }),
        }

class CuentaFijaForm(forms.ModelForm):
    class Meta:
        model = CuentaFija
        fields = ['nombre', 'saldo_actual']
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-slate-500 focus:border-slate-500 outline-hidden bg-white text-slate-900',
                'placeholder': 'Ej. Efectivo, Cuenta Nómina, Ahorros'
            }),
            'saldo_actual': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-slate-500 focus:border-slate-500 outline-hidden bg-white text-slate-900',
                'placeholder': '0.00',
                'step': '0.01'
            }),
        }