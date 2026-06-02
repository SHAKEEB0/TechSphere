from django.contrib import admin
from .models import SearchQuery, TrafficReport

@admin.register(TrafficReport)
class TrafficReportAdmin(admin.ModelAdmin):
    list_display = ('date', 'source', 'visitors', 'pageviews', 'sessions')
    list_filter = ('source',)
    search_fields = ('source',)

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ('query', 'hits', 'created_at')
    search_fields = ('query',)
