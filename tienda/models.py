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
    talles = models.CharField(max_length=100, blank=True, help_text="Ej: S, M, L o Único")
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    es_nuevo = models.BooleanField(default=True, verbose_name="¿Es Nuevo?")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre