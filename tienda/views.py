from django.shortcuts import render, get_object_or_404
from .models import Producto, Categoria, Portada
from django.db.models import Q
from django.core.paginator import Paginator

def catalogo(request, category_slug=None):
    category = None
    categorias = Categoria.objects.all()
    productos_list = Producto.objects.filter(activo=True).order_by('-id') 

    orden = request.GET.get('orden')

    if orden == 'min_precio':
        productos_list = productos_list.order_by('precio')
    elif orden == 'max_precio':
        productos_list = productos_list.order_by('-precio')
    elif orden == 'antiguos':
        productos_list = productos_list.order_by('id') 
    else:
        productos_list = productos_list.order_by('-id')

    # Lógica de Categorías
    if category_slug:
        category = get_object_or_404(Categoria, slug=category_slug)
        productos_list = productos_list.filter(categoria=category)
    
    # Buscador
    query = request.GET.get('q') 
    if query:
        productos_list = productos_list.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )

    paginator = Paginator(productos_list, 9) 
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number)

    try:
        portada = Portada.objects.get(activa=True).last()
    except:
        portada = None

    return render(request, 'tienda/catalogo.html', {
        'category': category,
        'categorias': categorias,
        'productos': productos
    })

def contacto(request):
    return render(request, 'tienda/contacto.html')

def nosotros(request):
    return render(request, 'tienda/nosotros.html')