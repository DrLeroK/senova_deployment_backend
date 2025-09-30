from rest_framework import serializers
from .models import (Category, Product, 
                     ProductVariant, ProductImage, 
                     HeadwearProduct, HeadwearImage,
                     ProductReview, HeadwearReview,
                     Order, OrderItem, Cart, CartItem)
import json

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'category_type', 'description', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'size', 'stock', 'low_stock_threshold', 'sku']
        read_only_fields = ['sku']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_featured', 'created_at']
        read_only_fields = ['created_at']


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    
    
    # WITH THIS FIELD:
    size_variants = serializers.CharField(
        write_only=True,
        required=False,
        help_text="JSON string of size variants with stock quantities"
    )

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_id', 'name', 'slug', 'description',
            'price', 'fabric', 'design_type', 'is_active', 'is_featured',
            'created_at', 'updated_at', 'variants', 'images', 
            'uploaded_images', 'size_variants'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def validate(self, data):
        # Handle JSON string parsing for size_variants
        size_variants = data.get('size_variants')
        
        if isinstance(size_variants, str):
            try:
                data['size_variants'] = json.loads(size_variants)
            except json.JSONDecodeError:
                raise serializers.ValidationError({
                    "size_variants": "Invalid JSON format for size variants."
                })
        
        # Now proceed with your existing validation
        category_id = data.get('category_id')
        size_variants = data.get('size_variants', [])
        
        print(f"DEBUG: category_id = {category_id}")
        print(f"DEBUG: size_variants = {size_variants}")
        print(f"DEBUG: type of size_variants = {type(size_variants)}")
        
        if category_id and not size_variants:
            raise serializers.ValidationError({
                "size_variants": "Size variants are required for clothing products."
            })
        
        # Validate each size variant
        if size_variants:
            for i, variant in enumerate(size_variants):
                print(f"DEBUG: variant {i} = {variant}")
                print(f"DEBUG: type of variant {i} = {type(variant)}")
                
                if not isinstance(variant, dict):
                    raise serializers.ValidationError({
                        "size_variants": f"Variant at index {i} must be a dictionary."
                    })
                
                if 'size' not in variant:
                    raise serializers.ValidationError({
                        "size_variants": f"Variant at index {i} must include a 'size' field."
                    })
                
                # Validate size value
                valid_sizes = [size[0] for size in Product.CLOTHING_SIZES]
                if variant['size'] not in valid_sizes:
                    raise serializers.ValidationError({
                        "size_variants": f"Invalid size '{variant['size']}' at index {i}. Valid sizes are: {valid_sizes}"
                    })
                
                # Validate stock value
                stock = variant.get('stock', 0)
                if not isinstance(stock, int) or stock < 0:
                    raise serializers.ValidationError({
                        "size_variants": f"Invalid stock value '{stock}' at index {i}. Stock must be a positive integer."
                    })
        
        return data

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        size_variants_data = validated_data.pop('size_variants', [])
        
        print("DEBUG: Creating product with validated_data:", validated_data)
        print("DEBUG: Size variants data:", size_variants_data)
        print("DEBUG: Number of images:", len(uploaded_images))
        
        product = Product.objects.create(**validated_data)
        print("DEBUG: Product created with ID:", product.id)
        
        # Create size variants
        variant_objects = []
        for i, variant_data in enumerate(size_variants_data):
            print(f"DEBUG: Creating variant {i}:", variant_data)
            try:
                variant = ProductVariant.objects.create(
                    product=product,
                    size=variant_data['size'],
                    stock=variant_data.get('stock', 0)
                )
                variant_objects.append(variant)
                print(f"DEBUG: Variant {i} created successfully")
            except Exception as e:
                print(f"DEBUG: Error creating variant {i}: {str(e)}")
                raise
        
        # Create images
        for i, image in enumerate(uploaded_images):
            print(f"DEBUG: Creating image {i}")
            ProductImage.objects.create(product=product, image=image)
        
        print("DEBUG: Product creation completed successfully")
        return product

    
    def update(self, instance, validated_data):
        request = self.context['request']
        
        # Process image deletions
        images_to_delete_ids = request.data.getlist('images_to_delete', [])
        if images_to_delete_ids:
            try:
                # Convert string IDs to integers and delete
                image_ids = [int(img_id) for img_id in images_to_delete_ids]
                instance.images.filter(id__in=image_ids).delete()
            except (ValueError, TypeError):
                pass  # Handle invalid IDs gracefully
        
        # Process new image uploads
        uploaded_images = request.FILES.getlist('uploaded_images')
        for image_file in uploaded_images:
            ProductImage.objects.create(
                product=instance, 
                image=image_file,
                alt_text=f"Image for {instance.name}"
            )
        
        # Process featured image if specified
        featured_image_id = request.data.get('featured_image')
        if featured_image_id and featured_image_id.isdigit():
            # Reset all images to not featured
            instance.images.update(is_featured=False)
            # Set the specified image as featured
            instance.images.filter(id=int(featured_image_id)).update(is_featured=True)
        
        # Handle size variants (existing code remains the same)
        size_variants_data = request.data.get('size_variants')
        if size_variants_data:
            try:
                size_variants = json.loads(size_variants_data)
                existing_variants = {variant.size: variant for variant in instance.variants.all()}
                
                for variant_data in size_variants:
                    size = variant_data['size']
                    stock = variant_data['stock']
                    
                    if size in existing_variants:
                        variant = existing_variants[size]
                        variant.stock = stock
                        variant.save()
                    else:
                        ProductVariant.objects.create(
                            product=instance,
                            size=size,
                            stock=stock
                        )
                
                requested_sizes = {v['size'] for v in size_variants}
                for variant in instance.variants.all():
                    if variant.size not in requested_sizes:
                        variant.delete()
                        
            except (json.JSONDecodeError, KeyError) as e:
                raise serializers.ValidationError({
                    'size_variants': 'Invalid size variants data format'
                })
        
        # Update other product fields
        return super().update(instance, validated_data)
    



#################### SERIALIZER FOR HEADWEAR MODELS ####################



class HeadwearImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeadwearImage
        fields = ['id', 'image', 'alt_text', 'is_featured', 'created_at']
        read_only_fields = ['created_at']


class HeadwearProductSerializer(serializers.ModelSerializer):
    images = HeadwearImageSerializer(many=True, read_only=True)
    
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = HeadwearProduct
        fields = [
            'id', 'name', 'slug', 'description', 'headwear_type', 'style',
            'material', 'price', 'stock', 'low_stock_threshold', 'is_active',
            'is_featured', 'created_at', 'updated_at', 'images', 'uploaded_images'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        headwear = HeadwearProduct.objects.create(**validated_data)
        
        # Create images
        for image in uploaded_images:
            HeadwearImage.objects.create(product=headwear, image=image)
        
        return headwear

    def update(self, instance, validated_data):
        request = self.context['request']
        
        # Process image deletions
        images_to_delete_ids = request.data.getlist('images_to_delete', [])
        if images_to_delete_ids:
            try:
                image_ids = [int(img_id) for img_id in images_to_delete_ids]
                instance.images.filter(id__in=image_ids).delete()
            except (ValueError, TypeError):
                pass
        
        # Process new image uploads
        uploaded_images = request.FILES.getlist('uploaded_images')
        for image_file in uploaded_images:
            HeadwearImage.objects.create(
                product=instance, 
                image=image_file,
                alt_text=f"Image for {instance.name}"
            )
        
        # Process featured image if specified
        featured_image_id = request.data.get('featured_image')
        if featured_image_id and featured_image_id.isdigit():
            instance.images.update(is_featured=False)
            instance.images.filter(id=int(featured_image_id)).update(is_featured=True)
        
        return super().update(instance, validated_data)


    

############################## REVIEW SERIALIZERS ###############################



class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'product', 'product_name', 'rating', 'comment', 'is_approved', 'created_at']
        read_only_fields = ['user', 'created_at']


class HeadwearReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = HeadwearReview
        fields = ['id', 'user', 'product', 'product_name', 'rating', 'comment', 'is_approved', 'created_at']
        read_only_fields = ['user', 'created_at']



############################## ORDER AND CART SERIALIZERS ###############################



class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    headwear_product_name = serializers.CharField(source='headwear_product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=8, decimal_places=2)
    headwear_product_price = serializers.DecimalField(source='headwear_product.price', read_only=True, max_digits=8, decimal_places=2)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'headwear_product', 'product_name', 'headwear_product_name', 
                 'product_price', 'headwear_product_price', 'quantity', 'size', 'total_price']
    
    def get_total_price(self, obj):
        return obj.total_price()

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_items', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']



class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    headwear_product_name = serializers.CharField(source='headwear_product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'headwear_product', 'product_name', 'headwear_product_name', 
                 'quantity', 'size', 'price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    delivery_method_display = serializers.CharField(source='get_delivery_method_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'order_number', 'status', 'status_display', 'delivery_method', 'delivery_method_display',
                 'customer_name', 'customer_email', 'customer_phone', 'address', 'city',
                 'state', 'zip_code', 'pickup_date', 'total_amount', 'is_paid',
                 'items', 'created_at', 'updated_at']
        read_only_fields = ['user', 'order_number', 'created_at', 'updated_at', 'customer_name', 'customer_email', 'total_amount']
