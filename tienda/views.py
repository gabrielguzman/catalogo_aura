from django.shortcuts import render, get_object_or_404
from .models import Producto, Categoria

def catalogo(request, category_slug=None):
    category = None
    categorias = Categoria.objects.all()
    
    # 1. Lógica de selección de categoría
    if category_slug:
        category = get_object_or_404(Categoria, slug=category_slug)
    else:
        category = Categoria.objects.filter(slug='lenceria').first()
        if not category:
            category = categorias.first()

    productos = Producto.objects.filter(categoria=category, activo=True)

    return render(request, 'tienda/catalogo.html', {
        'category': category,
        'categorias': categorias,
        'productos': productos
    })