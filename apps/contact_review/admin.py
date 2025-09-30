# contact_review/admin.py
from django.contrib import admin
from .models import ContactMessage, SiteReview

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']


@admin.register(SiteReview)
class SiteReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'title', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_featured', 'created_at']
    search_fields = ['user__username', 'user__email', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_approved', 'is_featured']