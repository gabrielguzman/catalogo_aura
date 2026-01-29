from django.shortcuts import render, get_object_or_404
from .models import Producto, Categoria, Portada, Pedido, DetallePedido, Cupon
from django.db.models import Q
from django.core.paginator import Paginator
from .carrito import Carrito
from django.contrib import messages
from django.shortcuts import redirect
from .forms import PedidoForm
from urllib.parse import quote

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
        'carrito': carrito,
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

# --- FUNCIÓN 1: APLICAR CUPÓN (La nueva) ---
def canjear_cupon(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        try:
            cupon = Cupon.objects.get(codigo__iexact=codigo, activo=True)
            request.session['cupon_id'] = cupon.id
            messages.success(request, f"¡Cupón {cupon.codigo} aplicado!")
        except Cupon.DoesNotExist:
            request.session['cupon_id'] = None
            messages.error(request, "El cupón no es válido.")
            
    return redirect('ver_carrito')


# --- FUNCIÓN 2: PROCESAR PEDIDO (La que se había perdido) ---
def procesar_pedido(request):
    carrito = Carrito(request)
    
    if carrito.obtener_cantidad_total() == 0:
        return redirect('catalogo')

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            # 1. Crear el pedido
            pedido = form.save(commit=False)
            pedido.total = carrito.obtener_total()
            pedido.save()

            # --- CONSTRUCCIÓN DEL MENSAJE ---
            detalle_texto = ""

            for item in carrito.carrito.values():
                producto = Producto.objects.get(id=item['producto_id'])
                
                # Guardar en Base de Datos
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item['cantidad'],
                    precio_unitario=float(item['precio'])
                )

                # Restar Stock
                producto.stock -= item['cantidad']
                producto.save()

                # Agregar al texto (Usamos \n para salto de línea)
                detalle_texto += f"- {item['cantidad']}x {producto.nombre}\n"

            # Cupón
            if carrito.obtener_descuento() > 0:
                detalle_texto += f"\n(Descuento aplicado: -${carrito.obtener_descuento()})\n"

            # 2. Limpiar Carrito
            carrito.limpiar()
            if 'cupon_id' in request.session:
                del request.session['cupon_id']

            # 3. Generar Link de WhatsApp Seguro
            numero_whatsapp = "3834084055" # <--- TU NÚMERO
            
            # Armamos el mensaje con saltos de línea normales
            mensaje_original = (
                f"Hola Aura! Soy {pedido.nombre_cliente}.\n"
                f"Hice el Pedido #{pedido.id} en la web:\n\n"
                f"{detalle_texto}\n"
                f"Total Final: ${pedido.total}\n\n"
                f"¿Cómo realizo el pago?"
            )
            
            # Codificamos el mensaje para que funcione en la URL (convierte espacios a %20, etc.)
            mensaje_codificado = quote(mensaje_original)
            
            url_wa = f"https://wa.me/{numero_whatsapp}?text={mensaje_codificado}"
            
            return redirect(url_wa)
    else:
        form = PedidoForm()

    return render(request, 'tienda/checkout.html', {
        'form': form,
        'carrito': carrito,
        'total': carrito.obtener_total()
    })
