from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.conf import settings

from django.core.validators import MinValueValidator, MaxValueValidator
import time


class Category(models.Model):
    CATEGORY_TYPES = [
        ('t_shirts', 'T-Shirts'),
        ('hoodies', 'Hoodies'),
        ('sweatshirts', 'Sweatshirts'),
        ('jackets', 'Jackets'),
        ('sweater', 'Sweater'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    # Size options applicable to clothing products
    CLOTHING_SIZES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('2XL', '2X Large'),
        ('3XL', '3X Large'),
    ]
    
    FABRICS = [
        ('cotton', '100% Cotton'),
        ('poly_cotton', 'Polyester-Cotton Blend'),
        ('polyester', '100% Polyester'),
        ('fleece', 'Fleece'),
        ('acrylic', 'Acrylic'),
        ('wool', 'Wool'),
        ('nylon', 'Nylon'),
        ('spandex', 'Spandex Blend'),
    ]
    
    category = models.ForeignKey(
        Category, 
        related_name='products', 
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    # Single price for all sizes
    price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(10)]
    )

    # Material/fabric composition
    fabric = models.CharField(
        max_length=20, 
        choices=FABRICS, 
        blank=True, 
        null=True
    )
    
    # For all clothing items
    design_type = models.CharField(
        max_length=20, 
        blank=True,
        choices=[
            ('graphic', 'Graphic Print'),
            ('embroidered', 'Embroidered'),
            ('plain', 'Plain'),
            ('pattern', 'Patterned'),
        ]
    )
    
    # Product status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def total_stock(self):
        """Calculate total stock across all size variants"""
        return sum(variant.stock for variant in self.variants.all())
        
    def is_low_stock(self):
        """Check if any variant is low on stock"""
        return any(variant.is_low_stock() for variant in self.variants.all())
        
    def available_sizes(self):
        """Return a list of sizes that are in stock"""
        return [variant.size for variant in self.variants.filter(stock__gt=0)]


class ProductVariant(models.Model):
    """
    Model for size-specific stock tracking (same price for all sizes)
    """
    product = models.ForeignKey(
        Product, 
        related_name='variants', 
        on_delete=models.CASCADE
    )
    size = models.CharField(max_length=10, choices=Product.CLOTHING_SIZES)
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    sku = models.CharField(max_length=50, unique=True, blank=True)
    
    class Meta:
        unique_together = ['product', 'size']
        
    def __str__(self):
        return f"{self.product.name} - {self.size} (Stock: {self.stock})"
        
    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold
        
    def save(self, *args, **kwargs):
        if not self.sku:
            # Generate SKU: first 3 letters of category + first 3 letters of product + size
            category_prefix = self.product.category.category_type[:3].upper()
            product_prefix = self.product.name[:3].upper()
            self.sku = f"{category_prefix}-{product_prefix}-{self.size}"
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        related_name='images', 
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Alternative text for accessibility"
    )
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"




############################### HEADWEAR DATABASE MODELS ################################


class HeadwearProduct(models.Model):
    # Headwear types
    HEADWEAR_TYPES = [
        ('caps', 'Caps'),
        ('hats', 'Hats'),
        ('beanies', 'Beanies'),
        ('headbands', 'Headbands'),
        ('visors', 'Visors'),
    ]
    
    MATERIALS = [
        ('cotton', '100% Cotton'),
        ('wool', 'Wool'),
        ('acrylic', 'Acrylic'),
        ('polyester', 'Polyester'),
        ('nylon', 'Nylon'),
        ('denim', 'Denim'),
        ('straw', 'Straw'),
        ('felt', 'Felt'),
    ]
    
    # Headwear styles
    HEADWEAR_STYLES = [
        ('baseball', 'Baseball Cap'),
        ('snapback', 'Snapback'),
        ('trucker', 'Trucker Hat'),
        ('bucket', 'Bucket Hat'),
        ('fedora', 'Fedora'),
        ('beanie', 'Beanie'),
        ('headband', 'Headband'),
        ('visor', 'Visor'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    headwear_type = models.CharField(max_length=20, choices=HEADWEAR_TYPES)
    style = models.CharField(max_length=20, choices=HEADWEAR_STYLES, blank=True)
    material = models.CharField(max_length=20, choices=MATERIALS, blank=True, null=True)
    
    price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(10)]
    )

    # Stock for headwear (no size variants, just total stock)
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    
    # Product status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['headwear_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def is_low_stock(self):
        """Check if product is low on stock"""
        return self.stock <= self.low_stock_threshold


class HeadwearImage(models.Model):
    product = models.ForeignKey(
        HeadwearProduct, 
        related_name='images', 
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='headwear_images/')
    alt_text = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Alternative text for accessibility"
    )
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"




################################## REVIEW MODELS ########################################


class ProductReview(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"


class HeadwearReview(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    product = models.ForeignKey(HeadwearProduct, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"




################################## CART & ORDER MODELS ########################################



class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    headwear_product = models.ForeignKey(HeadwearProduct, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product', 'size'], name='unique_product_cart_size'),
            models.UniqueConstraint(fields=['cart', 'headwear_product'], name='unique_headwear_cart')
        ]

    def __str__(self):
        if self.product:
            return f"{self.quantity} x {self.product.name} ({self.size})"
        return f"{self.quantity} x {self.headwear_product.name}"

    def total_price(self):
        if self.product:
            return self.quantity * self.product.price
        return self.quantity * self.headwear_product.price
    

class Order(models.Model):
    ORDER_STATUS = [
        ('new', 'New'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('picked_up', 'Picked Up'),
        ('failed', 'Failed'),  # Add this status
    ]
    
    DELIVERY_METHODS = [
        ('delivery', 'Delivery'),
        ('pickup', 'Pickup'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS)
    
    # Customer information
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    
    # Delivery/Pickup information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    pickup_date = models.DateTimeField(null=True, blank=True)
    
    # Payment information
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"

    # def save(self, *args, **kwargs):
    #     if not self.order_number:
    #         # Simple unique order number using UUID
    #         import uuid
    #         self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    #     super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if this is a new order
        
        if not self.order_number:
            # Simple unique order number using UUID
            import uuid
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        super().save(*args, **kwargs)
        
        # Create notification when order is created with status 'new'
        if is_new and self.status == 'new':
            OrderNotification.objects.create(order=self)

    def get_status_display(self):
        """Custom method to get status display name"""
        return dict(self.ORDER_STATUS).get(self.status, self.status)

    def get_delivery_method_display(self):
        """Custom method to get delivery method display name"""
        return dict(self.DELIVERY_METHODS).get(self.delivery_method, self.delivery_method)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    headwear_product = models.ForeignKey(HeadwearProduct, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    size = models.CharField(max_length=10, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.product:
            return f"{self.quantity} x {self.product.name} - ${self.price}"
        return f"{self.quantity} x {self.headwear_product.name} - ${self.price}"

    def total_price(self):
        return self.quantity * self.price




class OrderNotification(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for Order #{self.order.order_number}"
    