from django.contrib import admin
from .models import Advertisement, AffiliateLink, SponsoredPost

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('name', 'slot', 'active', 'created_at')
    list_filter = ('slot', 'active')
    search_fields = ('name', 'target_url')

@admin.register(AffiliateLink)
class AffiliateLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'affiliate_code', 'clicks', 'active')
    list_filter = ('active',)
    search_fields = ('title', 'affiliate_code')

@admin.register(SponsoredPost)
class SponsoredPostAdmin(admin.ModelAdmin):
    list_display = ('post', 'sponsor_name', 'sponsor_url')
    search_fields = ('post__title', 'sponsor_name')
