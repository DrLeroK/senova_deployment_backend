# contact_review/serializers.py
from rest_framework import serializers
from .models import ContactMessage, SiteReview
from django.contrib.auth import get_user_model

User = get_user_model()

class ContactMessageSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'subject', 'message', 
            'status', 'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SiteReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SiteReview
        fields = [
            'id', 'user', 'username', 'user_email', 'rating', 
            'title', 'comment', 'is_approved', 'is_featured',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class SiteReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteReview
        fields = ['rating', 'title', 'comment']


class SiteReviewAdminSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = SiteReview
        fields = [
            'id', 'user', 'user_email', 'rating', 'title', 'comment',
            'is_approved', 'is_featured', 'created_at', 'updated_at'
        ]