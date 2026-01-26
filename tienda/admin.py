from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Producto, Categoria, Portada

class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}

class ProductoAdmin(SummernoteModelAdmin):
    list_display = ('nombre', 'precio', 'categoria', 'talles', 'es_nuevo', 'activo')
    list_filter = ('categoria', 'activo', 'es_nuevo')
    search_fields = ('nombre', 'descripcion')

    summernote_fields = ('descripcion',)

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)
@admin.register(Portada)
class PortadaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'activa')
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return True