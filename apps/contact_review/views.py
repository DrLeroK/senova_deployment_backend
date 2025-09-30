# contact_review/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import ContactMessage, SiteReview
from .serializers import (
    ContactMessageSerializer, 
    SiteReviewSerializer,
    SiteReviewCreateSerializer,
    SiteReviewAdminSerializer
)


# Contact Message Views
class ContactMessageCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]


class ContactMessageListView(generics.ListAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = ContactMessage.objects.all()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset


class ContactMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ContactMessage.objects.all()


# Site Review Views
class SiteReviewListCreateView(generics.ListCreateAPIView):
    def get_queryset(self):
        return SiteReview.objects.filter(is_approved=True).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SiteReviewCreateSerializer
        return SiteReviewSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        # Check if user already has a review
        if SiteReview.objects.filter(user=self.request.user).exists():
            return Response(
                {"detail": "You have already submitted a review."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(user=self.request.user)


class SiteReviewDetailView(generics.RetrieveAPIView):
    queryset = SiteReview.objects.filter(is_approved=True)
    serializer_class = SiteReviewSerializer
    permission_classes = [permissions.AllowAny]


# Admin Views for Site Reviews
class AdminSiteReviewListView(generics.ListAPIView):
    serializer_class = SiteReviewAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = SiteReview.objects.all()
        
        # Filter by approval status
        approved = self.request.query_params.get('approved')
        if approved:
            if approved.lower() == 'true':
                queryset = queryset.filter(is_approved=True)
            elif approved.lower() == 'false':
                queryset = queryset.filter(is_approved=False)
                
        # Filter by featured status
        featured = self.request.query_params.get('featured')
        if featured:
            if featured.lower() == 'true':
                queryset = queryset.filter(is_featured=True)
            elif featured.lower() == 'false':
                queryset = queryset.filter(is_featured=False)
                
        return queryset.order_by('-created_at')


class AdminSiteReviewUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = SiteReviewAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = SiteReview.objects.all()


class AdminSiteReviewDeleteView(generics.DestroyAPIView):
    serializer_class = SiteReviewAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = SiteReview.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Review deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )