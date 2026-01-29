from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Categoria, Producto, Portada, ImagenProducto, Cupon

# 1. Configuración de Categorías
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1 
class ProductoAdmin(SummernoteModelAdmin):
    list_display = ('nombre', 'precio', 'categoria', 'talles', 'es_nuevo', 'activo')
    list_filter = ('categoria', 'activo', 'es_nuevo')
    search_fields = ('nombre', 'descripcion')
    
    summernote_fields = ('descripcion',)
    inlines = [ImagenProductoInline]
    prepopulated_fields = {'slug': ('nombre',)}

# 4. Registros
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)

@admin.register(Portada)
class PortadaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'activa')
    
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return True

@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descuento', 'activo')
    search_fields = ('codigo',)