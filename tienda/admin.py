from django.contrib import admin
from .models import Producto

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'activo') # Esto muestra columnas en la lista

admin.site.register(Producto, ProductoAdmin)