from django.shortcuts import render, get_object_or_404
from .models import Producto, Categoria, Portada, Pedido, DetallePedido, Cupon, Variante
from django.db.models import Q
from django.core.paginator import Paginator
from .carrito import Carrito
from django.contrib import messages
from django.shortcuts import redirect
from .forms import PedidoForm
from urllib.parse import quote
import urllib.parse

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

    if request.method == 'POST':
        color_id = request.POST.get('color_id')
        talle_id = request.POST.get('talle_id')

        if not color_id or not talle_id:
            messages.error(request, f"Por favor, selecciona un color y un talle para {producto.nombre}.")
            return redirect(request.META.get('HTTP_REFERER', 'catalogo'))

        try:
            variante = Variante.objects.get(
                producto=producto,
                color_id=color_id,
                talle_id=talle_id
            )
        except Variante.DoesNotExist:
            messages.error(request, "Esa combinación de color y talle no está disponible.")
            return redirect('catalogo')

        if variante.stock < 1:
            messages.warning(request, "¡Uy! Justo se agotó esa variante.")
            return redirect('catalogo')

        carrito.agregar(producto, variante) 
        messages.success(request, f'Agregado: {producto.nombre} ({variante.color} / {variante.talle}) 🛒')
    return redirect(request.META.get('HTTP_REFERER', 'catalogo'))

def eliminar_del_carrito(request, variante_id): # Recibimos variante_id
    carrito = Carrito(request)
    variante = get_object_or_404(Variante, id=variante_id) # Buscamos Variante
    carrito.eliminar(variante)
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

def sumar_carrito(request, variante_id):
    carrito = Carrito(request)
    # 1. Buscamos la VARIANTE específica (ej: Remera Roja Talle S)
    variante = get_object_or_404(Variante, id=variante_id)
    
    # 2. Obtenemos la cantidad actual de ESA variante en el carrito
    variante_id_str = str(variante.id)
    cantidad_actual = carrito.carrito.get(variante_id_str, {}).get('cantidad', 0)
    
    # 3. Validamos stock de la variante
    if cantidad_actual < variante.stock:
        # Ahora 'agregar' pide (producto, variante)
        carrito.agregar(variante.producto, variante)
    else:
        messages.warning(request, f'No hay más stock disponible de {variante.producto.nombre} en {variante.color} {variante.talle}')
        
    return redirect('ver_carrito')

def restar_carrito(request, variante_id):
    carrito = Carrito(request)
    variante = get_object_or_404(Variante, id=variante_id)
    
    carrito.restar(variante) # El método restar del carrito ya espera una variante
    return redirect('ver_carrito')

def eliminar_del_carrito(request, variante_id):
    carrito = Carrito(request)
    variante = get_object_or_404(Variante, id=variante_id)
    
    carrito.eliminar(variante) # El método eliminar ya espera una variante
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
    
    # Validación: Si no hay nada en el carrito, volver al catálogo
    if carrito.obtener_cantidad_total() == 0:
        return redirect('catalogo')

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            # 1. Guardar el Pedido (Cabecera)
            pedido = form.save(commit=False)
            pedido.total = carrito.obtener_total()
            pedido.save()

            # 2. Procesar ítems y armar el texto para WhatsApp
            # Usaremos una lista para ir guardando las líneas del mensaje
            lineas_productos = []
            
            for item in carrito.carrito.values():
                # Obtenemos la variante ID del carrito
                variante_id = item.get('variante_id')
                
                # Buscamos el objeto real en la BD para descontar stock
                try:
                    variante = Variante.objects.get(id=variante_id)
                    
                    # Descontamos stock
                    if variante.stock >= item['cantidad']:
                        variante.stock -= item['cantidad']
                        variante.save()
                    
                    # Guardamos el detalle en la base de datos
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=variante.producto,
                        variante=variante,
                        cantidad=item['cantidad'],
                        precio_unitario=float(item['precio'])
                    )
                    
                    # --- ARMADO DEL TEXTO PARA WHATSAPP ---
                    # Formato: "• Vestido Lino (Rojo M) x1"
                    # Usamos item['detalle'] que guardamos en el carrito.py, o lo sacamos de la variante
                    detalle_talle_color = f"{variante.color.nombre} {variante.talle.nombre}"
                    linea = f"• *{item['nombre']}* ({detalle_talle_color}) x{item['cantidad']}"
                    lineas_productos.append(linea)

                except Variante.DoesNotExist:
                    continue # Si por error no existe, saltamos para no romper todo

            # 3. Limpiar carrito después de procesar
            carrito.limpiar()

            # 4. Construir el mensaje final de WhatsApp
            # Unimos los productos con un salto de línea
            texto_productos_final = "\n".join(lineas_productos)
            
            mensaje_base = (
                f"Hola Aura! ✨\n"
                f"Soy *{pedido.nombre_cliente}* y quiero confirmar mi pedido *#{pedido.id}*.\n\n"
                f"📋 *Detalle del pedido:*\n"
                f"{texto_productos_final}\n\n"
                f"💰 *Total a pagar: ${pedido.total:,.0f}*\n"
                f"--------------------------------\n"
                f"Quedo a la espera de los datos para el pago. Gracias!"
            )

            # --- LA CLAVE MÁGICA ---
            # urllib.parse.quote convierte los espacios y enters en caracteres seguros para URL
            mensaje_codificado = urllib.parse.quote(mensaje_base)
            
            numero_whatsapp = "5493834084055" # Tu número sin espacios ni +
            url_whatsapp = f"https://wa.me/{numero_whatsapp}?text={mensaje_codificado}"

            return redirect(url_whatsapp)
            
    else:
        form = PedidoForm()

    return render(request, 'tienda/checkout.html', {'form': form, 'carrito': carrito})
