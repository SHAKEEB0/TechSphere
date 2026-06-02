from django.db import models
from django.urls import reverse

class Advertisement(models.Model):
    name = models.CharField(max_length=140)
    slot = models.CharField(max_length=60, choices=[
        ('header', 'Header'),
        ('sidebar', 'Sidebar'),
        ('footer', 'Footer'),
        ('in_article', 'In-Article'),
        ('mobile', 'Mobile'),
    ], default='sidebar')
    code_snippet = models.TextField(blank=True)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    target_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AffiliateLink(models.Model):
    title = models.CharField(max_length=180)
    url = models.URLField()
    affiliate_code = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    clicks = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def get_referral_url(self):
        return f'{self.url}?aff={self.affiliate_code}' if self.affiliate_code else self.url

    def __str__(self):
        return self.title

class SponsoredPost(models.Model):
    post = models.OneToOneField('blog.Post', on_delete=models.CASCADE, related_name='sponsored_details')
    sponsor_name = models.CharField(max_length=140)
    sponsor_url = models.URLField(blank=True)
    banner_image = models.ImageField(upload_to='sponsored/', blank=True, null=True)
    disclosure_text = models.CharField(max_length=255, default='Sponsored content')

    def __str__(self):
        return f'Sponsored: {self.post.title}'
