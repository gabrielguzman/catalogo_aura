from django import forms
from .models import Pedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nombre_cliente', 'telefono', 'email']
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Tu nombre completo',
                'required': 'true'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Tu celular (para WhatsApp)',
                'required': 'true'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Tu email (opcional)'
            }),
        }