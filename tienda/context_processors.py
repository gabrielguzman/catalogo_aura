from .carrito import Carrito

def carrito_total(request):
    """
    Hace disponible la cantidad de ítems del carrito para el ícono rojo del menú.
    """
    carrito = Carrito(request)
    return {'cantidad_carrito': carrito.obtener_cantidad_total()}