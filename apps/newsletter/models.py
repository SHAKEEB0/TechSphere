from django.db import models
from django.urls import reverse

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=80, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('newsletter:subscriber_detail', args=[self.pk])

class NewsletterCampaign(models.Model):
    subject = models.CharField(max_length=255)
    content = models.TextField()
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.subject
