class Carrito:
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            carrito = self.session['carrito'] = {}
        self.carrito = carrito
    
    def agregar(self, producto):
        producto_id = str(producto.id)
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {
                'producto_id': producto.id,         # IMPORTANTE: Para los links de eliminar/sumar
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'cantidad': 1,
                'imagen': producto.imagen.url if producto.imagen else '', # IMPORTANTE: Para la foto
                'stock': producto.stock             # IMPORTANTE: Para validar el límite
            }
        else:
            # Solo sumamos si no superamos el stock (doble validación por seguridad)
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
    
    def limpiar(self):
        self.session['carrito'] = {}
        self.guardar()
    
    def obtener_total(self):
        total = 0
        for item in self.carrito.values():
            total += float(item['precio']) * item['cantidad']
        return total
    
    def obtener_cantidad_total(self):
        return sum(item['cantidad'] for item in self.carrito.values())
    
    def restar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            self.carrito[producto_id]['cantidad'] -= 1
            if self.carrito[producto_id]['cantidad'] < 1:
                self.eliminar(producto)
            else:
                self.guardar()