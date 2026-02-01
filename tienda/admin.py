from django.contrib import admin
from .models import Categoria, Producto, Variante, ImagenProducto, Color, Talle, Portada, Cupon, Pedido, DetallePedido

admin.site.register(Categoria)
admin.site.register(Color)
admin.site.register(Talle)
admin.site.register(Portada)

@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descuento', 'activo')
    search_fields = ('codigo',)

# PRODUCTOS Y VARIANTES
class VarianteInline(admin.TabularInline):
    model = Variante
    extra = 1 
    min_num = 0
class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'get_stock_total', 'activo')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre',)
    
    inlines = [VarianteInline, ImagenProductoInline] 

# PEDIDOS Y DETALLES
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'variante', 'cantidad', 'precio_unitario')
    can_delete = False

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'telefono', 'total', 'fecha', 'pagado')
    list_filter = ('pagado', 'fecha')
    search_fields = ('nombre_cliente', 'email', 'telefono', 'id')
    readonly_fields = ('fecha', 'total')
    inlines = [DetallePedidoInline]