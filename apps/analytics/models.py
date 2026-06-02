from django.db import models

class TrafficReport(models.Model):
    date = models.DateField()
    visitors = models.PositiveIntegerField(default=0)
    pageviews = models.PositiveIntegerField(default=0)
    sessions = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('date', 'source')

    def __str__(self):
        return f'{self.date} - {self.source or "organic"}'

class SearchQuery(models.Model):
    query = models.CharField(max_length=255)
    hits = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query
