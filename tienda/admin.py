from django.contrib import admin
from .models import Producto, Categoria, Portada

class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'categoria', 'talles', 'es_nuevo', 'activo')
    list_filter = ('categoria', 'activo', 'es_nuevo')
    search_fields = ('nombre', 'descripcion')

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)
@admin.register(Portada)
class PortadaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'activa')
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return True