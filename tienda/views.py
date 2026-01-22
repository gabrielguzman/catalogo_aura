from django.shortcuts import render
from .models import Producto

def catalogo(request):
    productos = Producto.objects.filter(activo=True)
    return render(request, 'tienda/catalogo.html', {'productos': productos})
