from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction, models
from .models import (Category, Product, 
                     HeadwearProduct, Order, 
                     ProductReview, HeadwearReview,
                     OrderItem, Cart, OrderNotification, 
                     CartItem, ProductVariant)

from .serializers import (CategorySerializer, ProductSerializer, 
                          HeadwearProductSerializer, OrderSerializer,
                          ProductReviewSerializer, HeadwearReviewSerializer,
                          CartSerializer, CartItemSerializer
                          )
import json
from rest_framework import serializers


############################## MODEL FOR REVIEWS ###############################

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

class PublicCategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


################################ PRODUCT VIEWS #################################


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related('category').prefetch_related('images', 'variants')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()
        

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category').prefetch_related('images', 'variants')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    @transaction.atomic
    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Product deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
    



class PublicProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'variants')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category if provided
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            
        # Filter by featured products if requested
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
            
        # Add search functionality
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(name__icontains=search_query) |
                models.Q(description__icontains=search_query) |
                models.Q(category__name__icontains=search_query)
            )
            
        return queryset
    
    

class PublicProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'variants')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'



############################ VIEWS FOR HEADWEAR MODELS ###########################



class HeadwearListCreateView(generics.ListCreateAPIView):
    queryset = HeadwearProduct.objects.prefetch_related('images')
    serializer_class = HeadwearProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()

class HeadwearRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HeadwearProduct.objects.prefetch_related('images')
    serializer_class = HeadwearProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    @transaction.atomic
    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Headwear product deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )



class PublicHeadwearListView(generics.ListAPIView):
    queryset = HeadwearProduct.objects.filter(is_active=True).prefetch_related('images')
    serializer_class = HeadwearProductSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by headwear type if provided
        headwear_type = self.request.query_params.get('headwear_type')
        if headwear_type:
            queryset = queryset.filter(headwear_type=headwear_type)
            
        # Filter by featured products if requested
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
            
        # Add search functionality
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(name__icontains=search_query) |
                models.Q(description__icontains=search_query) |
                models.Q(headwear_type__icontains=search_query)
            )
            
        return queryset
    


# Create a dedicated search view that searches across both product types
class GlobalSearchView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]

    # Add a basic serializer to fix the schema generation
    def get_serializer_class(self):
        from rest_framework import serializers
        return serializers.Serializer
    
    def get(self, request, *args, **kwargs):
        search_query = request.query_params.get('q', '')
        
        if not search_query:
            return Response({
                'clothing_products': [],
                'headwear_products': [],
                'total_results': 0
            })
        
        # Search in clothing products
        clothing_products = Product.objects.filter(
            is_active=True,
        ).filter(
            models.Q(name__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(category__name__icontains=search_query)
        ).select_related('category').prefetch_related('images', 'variants')[:10]  # Limit results
        
        # Search in headwear products
        headwear_products = HeadwearProduct.objects.filter(
            is_active=True,
        ).filter(
            models.Q(name__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(headwear_type__icontains=search_query)
        ).prefetch_related('images')[:10]  # Limit results
        
        # Serialize results
        clothing_serializer = ProductSerializer(clothing_products, many=True)
        headwear_serializer = HeadwearProductSerializer(headwear_products, many=True)
        
        total_results = len(clothing_products) + len(headwear_products)
        
        return Response({
            'clothing_products': clothing_serializer.data,
            'headwear_products': headwear_serializer.data,
            'total_results': total_results,
            'search_query': search_query
        })
    


class PublicHeadwearDetailView(generics.RetrieveAPIView):
    queryset = HeadwearProduct.objects.filter(is_active=True).prefetch_related('images')
    serializer_class = HeadwearProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'



################################## REVIEW MODELS ################################


class AdminProductReviewListView(generics.ListAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return ProductReview.objects.all().order_by('-created_at')


class AdminProductReviewUpdateView(generics.UpdateAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ProductReview.objects.all()


class AdminHeadwearReviewListView(generics.ListAPIView):
    serializer_class = HeadwearReviewSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return HeadwearReview.objects.all().order_by('-created_at')


class AdminHeadwearReviewUpdateView(generics.UpdateAPIView):
    serializer_class = HeadwearReviewSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = HeadwearReview.objects.all()

# client side 
class ProductReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return ProductReview.objects.filter(is_approved=True, product__is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class HeadwearReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = HeadwearReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return HeadwearReview.objects.filter(is_approved=True, product__is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



################################  ORDER VIEWS  #################################


class AdminOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        status = self.request.query_params.get('status')
        queryset = Order.objects.all().order_by('-created_at')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

class AdminOrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.all()


##################### CUSTOMER SIDE CART AND ORDER VIEWS ###########################

class CartDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

class CartItemCreateView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

class CartItemUpdateView(generics.UpdateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Add Swagger fake view check
        if getattr(self, 'swagger_fake_view', False):
            return CartItem.objects.none()
        return CartItem.objects.filter(cart__user=self.request.user)

class CartItemDestroyView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Add Swagger fake view check
        if getattr(self, 'swagger_fake_view', False):
            return CartItem.objects.none()
        return CartItem.objects.filter(cart__user=self.request.user)


# Customer Order Views
class PublicOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Add Swagger fake view check
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class PublicOrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Add Swagger fake view check
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def perform_create(self, serializer):
        # Get user's cart
        cart = Cart.objects.get(user=self.request.user)
        cart_items = cart.items.all()
        
        if not cart_items:
            raise serializers.ValidationError("Cannot create order with empty cart")
        
        # Calculate total amount
        total_amount = sum(item.total_price() for item in cart_items)
        
        # Create order
        order = serializer.save(
            user=self.request.user,
            total_amount=total_amount,
            customer_name=f"{self.request.user.first_name} {self.request.user.last_name}",
            customer_email=self.request.user.email
        )
        
        # Create order items from cart items AND reduce stock
        for cart_item in cart_items:
            if cart_item.product:
                # For clothing products with size variants
                try:
                    # Find the specific size variant
                    variant = ProductVariant.objects.get(
                        product=cart_item.product, 
                        size=cart_item.size
                    )
                    # Check if enough stock exists
                    if variant.stock < cart_item.quantity:
                        raise serializers.ValidationError(
                            f"Not enough stock for {cart_item.product.name} in size {cart_item.size}"
                        )
                    # Reduce stock
                    variant.stock -= cart_item.quantity
                    variant.save()
                except ProductVariant.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Size variant not found for {cart_item.product.name}"
                    )
                
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    size=cart_item.size,
                    price=cart_item.product.price
                )
            elif cart_item.headwear_product:
                # For headwear products (no size variants)
                if cart_item.headwear_product.stock < cart_item.quantity:
                    raise serializers.ValidationError(
                        f"Not enough stock for {cart_item.headwear_product.name}"
                    )
                
                # Reduce headwear stock
                cart_item.headwear_product.stock -= cart_item.quantity
                cart_item.headwear_product.save()
                
                OrderItem.objects.create(
                    order=order,
                    headwear_product=cart_item.headwear_product,
                    quantity=cart_item.quantity,
                    price=cart_item.headwear_product.price
                )
        
        # Clear the cart after successful order creation
        cart.items.all().delete()
        
        return order
    


    

####### View to get count of new orders and unread notifications ####

class NewOrderCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Check if user is staff/admin
        if not request.user.is_staff:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        new_order_count = Order.objects.filter(status='new').count()
        unread_notifications_count = OrderNotification.objects.filter(is_read=False).count()
        
        return Response({
            'new_orders_count': new_order_count,
            'unread_notifications_count': unread_notifications_count
        })

class MarkNotificationAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, order_id):
        # Check if user is staff/admin
        if not request.user.is_staff:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Get the order first to ensure it exists
            order = Order.objects.get(id=order_id)
            
            # Try to get the notification for this order
            notification, created = OrderNotification.objects.get_or_create(
                order=order,
                defaults={'is_read': True}
            )
            
            # Mark as read
            notification.is_read = True
            notification.save()
            
            return Response({"success": True, "message": "Notification marked as read"})
            
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
