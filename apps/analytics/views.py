from django.shortcuts import render
from django.views.generic import TemplateView

class DashboardView(TemplateView):
    template_name = 'analytics/dashboard.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})
