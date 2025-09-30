from django.contrib import admin
from .models import Category, Product, ProductVariant, ProductImage

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['size', 'stock', 'low_stock_threshold', 'sku']
    readonly_fields = ['sku']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_featured']
    readonly_fields = ['created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'slug', 'created_at']
    list_filter = ['category_type', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'fabric', 'is_active', 'is_featured', 'created_at']
    list_filter = ['category', 'fabric', 'design_type', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'total_stock', 'available_sizes']
    inlines = [ProductVariantInline, ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'slug', 'description', 'price')
        }),
        ('Product Details', {
            'fields': ('fabric', 'design_type')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'total_stock', 'available_sizes'),
            'classes': ('collapse',)
        })
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'stock', 'low_stock_threshold', 'sku', 'is_low_stock']
    list_filter = ['size', 'stock']
    search_fields = ['product__name', 'sku']
    readonly_fields = ['sku', 'is_low_stock']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'is_featured', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['product__name', 'alt_text']
    readonly_fields = ['created_at']