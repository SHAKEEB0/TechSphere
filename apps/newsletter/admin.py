from django.contrib import admin
from .models import NewsletterCampaign, NewsletterSubscriber

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'subscribed_at', 'is_active', 'source')
    search_fields = ('email', 'first_name', 'source')
    list_filter = ('is_active',)

@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = ('subject', 'is_sent', 'sent_at', 'created_at')
    search_fields = ('subject',)
    readonly_fields = ('created_at',)
