from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, null=True, blank=True) 
    class Meta:
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio Anterior (Tachado)")
    talles = models.CharField(max_length=100, blank=True, help_text="Ej: S, M, L o Único")
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    es_nuevo = models.BooleanField(default=True, verbose_name="¿Es Nuevo?")
    stock = models.IntegerField(default=0, verbose_name="Stock Disponible")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
    def get_descuento(self):
        if self.precio_anterior and self.precio_anterior > self.precio:
            descuento = 100 - (self.precio / self.precio_anterior * 100)
            return int(descuento)
        return 0

    def tiene_stock(self):
        return self.stock > 0

class Portada(models.Model):
    titulo = models.CharField(max_length=100, default="Tu Estilo, Tu Aura")
    subtitulo = models.CharField(max_length=200, blank=True, null=True, help_text="Ej: Colección Otoño/Invierno")
    texto_boton = models.CharField(max_length=50, default="Ver Productos")
    imagen = models.ImageField(upload_to='portadas/', help_text="Idealmente una imagen horizontal de alta calidad")
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Configuración de Portada"
        verbose_name_plural = "Configuración de Portada"

    def __str__(self):
        return self.titulo