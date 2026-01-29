from .models import Cupon # <--- IMPORTANTE: Importar el modelo

class Carrito:
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            carrito = self.session['carrito'] = {}
        self.carrito = carrito
        # Leemos si hay un cupón en la sesión
        self.cupon_id = self.session.get('cupon_id')

    def agregar(self, producto):
        producto_id = str(producto.id)
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {
                'producto_id': producto.id,
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'cantidad': 1,
                'imagen': producto.imagen.url if producto.imagen else '',
                'stock': producto.stock
            }
        else:
            if self.carrito[producto_id]['cantidad'] < producto.stock:
                self.carrito[producto_id]['cantidad'] += 1
        self.guardar()

    def guardar(self):
        self.session.modified = True

    def eliminar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar()

    def restar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            self.carrito[producto_id]['cantidad'] -= 1
            if self.carrito[producto_id]['cantidad'] < 1:
                self.eliminar(producto)
            else:
                self.guardar()

    def limpiar(self):
        self.session['carrito'] = {}
        # Opcional: ¿Quieres borrar el cupón también al limpiar?
        # self.session['cupon_id'] = None 
        self.guardar()

    def obtener_subtotal(self):
        """Suma de precios sin descuento"""
        total = 0
        for item in self.carrito.values():
            total += float(item['precio']) * item['cantidad']
        return total

    def obtener_descuento(self):
        """Calcula cuánto dinero se descuenta"""
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
        """Subtotal - Descuento"""
        return self.obtener_subtotal() - self.obtener_descuento()
    
    def obtener_cantidad_total(self):
        return sum(item['cantidad'] for item in self.carrito.values())