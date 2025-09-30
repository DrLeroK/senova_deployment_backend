from django.urls import path
from .views import (
    ContactMessageCreateView,
    ContactMessageListView,
    ContactMessageDetailView,
    SiteReviewListCreateView,
    SiteReviewDetailView,
    AdminSiteReviewListView,
    AdminSiteReviewUpdateView,
    AdminSiteReviewDeleteView,
)

urlpatterns = [
    # Public Contact Message Endpoints
    path('contact/', ContactMessageCreateView.as_view(), name='contact-message-create'),
    
    # Public Site Review Endpoints
    path('reviews/', SiteReviewListCreateView.as_view(), name='site-review-list-create'),
    path('reviews/<int:pk>/', SiteReviewDetailView.as_view(), name='site-review-detail'),
    
    # Admin Contact Message Endpoints
    path('admin/contact-messages/', ContactMessageListView.as_view(), name='admin-contact-message-list'),
    path('admin/contact-messages/<int:pk>/', ContactMessageDetailView.as_view(), name='admin-contact-message-detail'),
    
    # Admin Site Review Endpoints
    path('admin/site-reviews/', AdminSiteReviewListView.as_view(), name='admin-site-review-list'),
    path('admin/site-reviews/<int:pk>/', AdminSiteReviewUpdateView.as_view(), name='admin-site-review-update'),
    path('admin/site-reviews/<int:pk>/delete/', AdminSiteReviewDeleteView.as_view(), name='admin-site-review-delete'),
]