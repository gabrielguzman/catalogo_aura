from django.shortcuts import render, get_object_or_404
from .models import Producto, Categoria, Portada
from django.db.models import Q
from django.core.paginator import Paginator
from .carrito import Carrito
from django.contrib import messages
from django.shortcuts import redirect

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

def agregar_al_carrito(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    carrito.agregar(producto)
    messages.success(request, f'¡Agregamos "{producto.nombre}" al carrito! 🛒')
    return redirect('catalogo')

def eliminar_del_carrito(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    carrito.eliminar(producto)
    messages.warning(request, 'Producto eliminado.')
    return redirect('ver_carrito')

def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect('catalogo')

def ver_carrito(request):
    carrito = Carrito(request)
    # Convertimos el diccionario a lista para usarlo fácil en el template
    items = carrito.carrito.values()
    total = carrito.obtener_total()
    
    # Armamos el texto para WhatsApp
    texto_wa = "Hola! Quiero confirmar este pedido:%0A"
    for item in items:
        texto_wa += f"- {item['cantidad']}x {item['nombre']} (${item['precio']})%0A"
    texto_wa += f"%0A*Total Estimado: ${total}*"
    
    return render(request, 'tienda/carrito.html', {
        'items': items,
        'total': total,
        'texto_wa': texto_wa
    })

def sumar_carrito(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Validamos stock antes de sumar
    producto_id_str = str(producto_id)
    cantidad_actual = carrito.carrito.get(producto_id_str, {}).get('cantidad', 0)
    print("Cantidad actual en carrito:", cantidad_actual)
    
    if cantidad_actual < producto.stock:
        carrito.agregar(producto)
    else:
        messages.warning(request, f'No hay más stock disponible de {producto.nombre}')
        
    return redirect('ver_carrito')

def restar_carrito(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    carrito.restar(producto)
    return redirect('ver_carrito')