from django.urls import path
from .views import (
    CategoryListCreateView, CategoryRetrieveUpdateDestroyView,
    ProductListCreateView, ProductRetrieveUpdateDestroyView,
    PublicProductListView, PublicProductDetailView,
    PublicCategoryListView, HeadwearListCreateView,
    HeadwearRetrieveUpdateDestroyView, PublicHeadwearListView,
    PublicHeadwearDetailView,

    AdminProductReviewListView, AdminProductReviewUpdateView, 
    AdminHeadwearReviewListView, AdminHeadwearReviewUpdateView, 
    ProductReviewListCreateView, HeadwearReviewListCreateView,

    AdminOrderListView, AdminOrderDetailView,

    CartDetailView, CartItemCreateView,
    CartItemUpdateView, CartItemDestroyView,

    PublicOrderListView, PublicOrderDetailView,
    OrderCreateView,

    GlobalSearchView,

    NewOrderCountView, MarkNotificationAsReadView,

)

urlpatterns = [

    # Category endpoints
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),

    # Public category endpoints
    path('public/categories/', PublicCategoryListView.as_view(), name='public-category-list'),
    
    # Product endpoints (admin only)
    path('private/products/', ProductListCreateView.as_view(), name='product-list'),
    path('private/products/<slug:slug>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
    
    # Public product endpoints (for customers)
    path('public/products/', PublicProductListView.as_view(), name='public-product-list'),
    path('public/products/<slug:slug>/', PublicProductDetailView.as_view(), name='public-product-detail'),


    #################  NEW ADDED URLS ##################
    
    # Headwear endpoints (admin only)
    path('private/headwear/', HeadwearListCreateView.as_view(), name='headwear-list'),
    path('private/headwear/<slug:slug>/', HeadwearRetrieveUpdateDestroyView.as_view(), name='headwear-detail'),
    
    # Public headwear endpoints (for customers)
    path('public/headwear/', PublicHeadwearListView.as_view(), name='public-headwear-list'),
    path('public/headwear/<slug:slug>/', PublicHeadwearDetailView.as_view(), name='public-headwear-detail'),

    # Admin Review Endpoints (Private)
    path('admin/reviews/products/', AdminProductReviewListView.as_view(), name='admin-product-review-list'),
    path('admin/reviews/products/<int:pk>/', AdminProductReviewUpdateView.as_view(), name='admin-product-review-update'),
    path('admin/reviews/headwear/', AdminHeadwearReviewListView.as_view(), name='admin-headwear-review-list'),
    path('admin/reviews/headwear/<int:pk>/', AdminHeadwearReviewUpdateView.as_view(), name='admin-headwear-review-update'),
    
    # Public Review Endpoints (Client Side)
    path('products/<int:product_id>/reviews/', ProductReviewListCreateView.as_view(), name='product-reviews'),
    path('headwear/<int:headwear_id>/reviews/', HeadwearReviewListCreateView.as_view(), name='headwear-reviews'),
    
    ############################### ORDER URLS ###############################
    
    # Admin Order Endpoints (Private)
    path('admin/orders/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/orders/<int:pk>/', AdminOrderDetailView.as_view(), name='admin-order-detail'),
    
    # Public Order Endpoints (Client Side)
    path('orders/', OrderCreateView.as_view(), name='order-create'),
    path('orders/my-orders/', PublicOrderListView.as_view(), name='public-order-list'),
    # path('orders/my-orders/<int:pk>/', PublicOrderDetailView.as_view(), name='public-order-detail'),
    path('orders/my-orders/<int:pk>/', PublicOrderDetailView.as_view(), name='public-order-detail'),  # Changed from <int:order_id> to <int:pk>
    
    ############################### CART URLS ###############################
    
    # Cart Endpoints (Client Side - Authenticated Users)
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/items/', CartItemCreateView.as_view(), name='cart-item-create'),
    path('cart/items/<int:pk>/', CartItemUpdateView.as_view(), name='cart-item-update'),
    path('cart/items/<int:pk>/delete/', CartItemDestroyView.as_view(), name='cart-item-delete'),

    path('public/search/', GlobalSearchView.as_view(), name='global-search'),


    # Notification endpoints
    path('admin/orders/new-order-count/', NewOrderCountView.as_view(), name='new-order-count'),
    path('admin/orders/<int:order_id>/mark-notification-read/', MarkNotificationAsReadView.as_view(), name='mark-notification-read'),

    # path('admin/orders/new-order-count/', NewOrderCountView.as_view(), name='new-order-count'),
    # path('admin/orders/<int:order_id>/mark-notification-read/', MarkNotificationAsReadView.as_view(), name='mark-notification-read'),

]

