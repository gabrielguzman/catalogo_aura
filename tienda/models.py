from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# --- 1. MAESTROS DE ATRIBUTOS ---

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, null=True, blank=True) 
    class Meta:
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

class Talle(models.Model):
    nombre = models.CharField(max_length=50, help_text="Ej: S, M, L, 40, 42, Único")
    
    def __str__(self):
        return self.nombre

class Color(models.Model):
    nombre = models.CharField(max_length=50, help_text="Ej: Rojo, Blanco, Estampado Floral")
    codigo_hex = models.CharField(max_length=7, blank=True, null=True, help_text="Opcional: Código de color (ej: #FF0000) para mostrar la bolita de color")

    class Meta:
        verbose_name_plural = "Colores"

    def __str__(self):
        return self.nombre

# --- 2. EL PRODUCTO (PADRE) ---

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Usamos 'imagen' para mantener compatibilidad con tus templates actuales
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True, verbose_name="Imagen de Portada")
    
    es_nuevo = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
    def get_descuento(self):
        if self.precio_anterior and self.precio_anterior > self.precio:
            descuento = 100 - (self.precio / self.precio_anterior * 100)
            return int(descuento)
        return 0

    # Método clave: El stock total es la suma de las variantes
    def get_stock_total(self):
        total = sum(variante.stock for variante in self.variantes.all())
        return total

    def tiene_stock(self):
        return self.get_stock_total() > 0
    
    def get_relacionados(self):
        return Producto.objects.filter(categoria=self.categoria, activo=True).exclude(id=self.id).order_by('-id')[:3]

# --- 3. LAS VARIANTES (HIJOS - Aquí vive el Stock) ---

class Variante(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='variantes')
    color = models.ForeignKey(Color, on_delete=models.PROTECT)
    talle = models.ForeignKey(Talle, on_delete=models.PROTECT)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('producto', 'color', 'talle') # Evita duplicados (Ej: dos veces Rojo S)

    def __str__(self):
        return f"{self.producto.nombre} - {self.color} / {self.talle}"

# --- 4. IMÁGENES EXTRA ---

class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos_extra/')
    # Opcional: Foto específica para un color
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Foto de {self.producto.nombre}"

# --- 5. CONFIGURACIÓN Y MARKETING ---

class Portada(models.Model):
    titulo = models.CharField(max_length=100, default="Tu Estilo, Tu Aura")
    subtitulo = models.CharField(max_length=200, blank=True, null=True)
    texto_boton = models.CharField(max_length=50, default="Ver Productos")
    imagen = models.ImageField(upload_to='portadas/')
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Configuración de Portada"
        verbose_name_plural = "Configuración de Portada"

    def __str__(self):
        return self.titulo

class Cupon(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descuento = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje de descuento (0 a 100)"
    )
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.codigo} ({self.descuento}%)"

# --- 6. PEDIDOS Y VENTAS ---

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
    # Mantenemos producto para referencia rápida
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    # Agregamos variante para saber EXACTAMENTE qué se llevó (y descontar stock)
    variante = models.ForeignKey(Variante, on_delete=models.SET_NULL, null=True, blank=True)
    
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        detalle = f"{self.cantidad}x {self.producto.nombre}"
        if self.variante:
            detalle += f" ({self.variante.color} {self.variante.talle})"
        return detalle