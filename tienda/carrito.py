from .models import Cupon

class Carrito:
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            carrito = self.session['carrito'] = {}
        self.carrito = carrito
        self.cupon_id = self.session.get('cupon_id')

    # MODIFICADO: Ahora recibe también la 'variante'
    def agregar(self, producto, variante):
        # Usamos el ID de la VARIANTE como clave única (para distinguir Rojo de Azul)
        id_unico = str(variante.id)
        
        if id_unico not in self.carrito:
            self.carrito[id_unico] = {
                'producto_id': producto.id,
                'variante_id': variante.id, # Guardamos esto para saber qué descontar luego
                'nombre': producto.nombre,
                # Guardamos el detalle para mostrarlo en el HTML (Ej: "Rojo / S")
                'detalle': f"{variante.color.nombre} - {variante.talle.nombre}",
                'precio': str(producto.precio),
                'cantidad': 1,
                'imagen': producto.imagen.url if producto.imagen else '',
                # IMPORTANTE: El stock límite es el de la variante, no del producto general
                'stock': variante.stock 
            }
        else:
            # Solo sumamos si no supera el stock de esa variante específica
            if self.carrito[id_unico]['cantidad'] < variante.stock:
                self.carrito[id_unico]['cantidad'] += 1
                
        self.guardar()

    def guardar(self):
        self.session.modified = True

    # MODIFICADO: Ahora elimina buscando por variante
    def eliminar(self, variante):
        id_unico = str(variante.id)
        if id_unico in self.carrito:
            del self.carrito[id_unico]
            self.guardar()

    # MODIFICADO: Resta buscando por variante
    def restar(self, variante):
        id_unico = str(variante.id)
        if id_unico in self.carrito:
            self.carrito[id_unico]['cantidad'] -= 1
            if self.carrito[id_unico]['cantidad'] < 1:
                self.eliminar(variante)
            else:
                self.guardar()

    def limpiar(self):
        self.session['carrito'] = {}
        self.guardar()

    def obtener_subtotal(self):
        total = 0
        for item in self.carrito.values():
            total += float(item['precio']) * item['cantidad']
        return total

    def obtener_descuento(self):
        subtotal = self.obtener_subtotal()
        descuento = 0
        if self.cupon_id:
            try:
                cupon = Cupon.objects.get(id=self.cupon_id, activo=True)
                descuento = (subtotal * cupon.descuento) / 100
            except Cupon.DoesNotExist:
                pass
        return descuento

    def obtener_total(self):
        return self.obtener_subtotal() - self.obtener_descuento()
    
    def obtener_cantidad_total(self):
        return sum(item['cantidad'] for item in self.carrito.values())