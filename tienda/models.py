from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, null=True, blank=True) 
    class Meta:
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=True, blank=True)
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
    
    def get_relacionados(self):
        return Producto.objects.filter(categoria=self.categoria, activo=True, stock__gt=0).exclude(id=self.id).order_by('-id')[:3]

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

class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes_extra')
    imagen = models.ImageField(upload_to='productos_extra/')

    def __str__(self):
        return f"Foto extra de {self.producto.nombre}"
    
class Cupon(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descuento = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje de descuento (0 a 100)"
    )
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.codigo} ({self.descuento}%)"
    
class Pedido(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"Pedido #{self.id} - {self.nombre_cliente}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"