from django.shortcuts import render, get_object_or_404
from .models import Producto, Categoria
from django.db.models import Q

def catalogo(request, category_slug=None):
    category = None
    categorias = Categoria.objects.all()
    productos = Producto.objects.filter(activo=True)

    if category_slug:
        category = get_object_or_404(Categoria, slug=category_slug)
        productos = productos.filter(categoria=category)
    
    query = request.GET.get('q') # 'q' es lo que escribe el usuario en la cajita
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )

    return render(request, 'tienda/catalogo.html', {
        'category': category,
        'categorias': categorias,
        'productos': productos
    })

def contacto(request):
    return render(request, 'tienda/contacto.html')

def nosotros(request):
    return render(request, 'tienda/nosotros.html')