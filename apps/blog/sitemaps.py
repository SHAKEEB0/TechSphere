from django.contrib.sitemaps import Sitemap
from .models import Category, Post, Tag

class PostSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Post.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

class CategorySitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Category.objects.all()

class TagSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return Tag.objects.all()
