from django.shortcuts import render
from django.views.generic import TemplateView

class AdOverviewView(TemplateView):
    template_name = 'ads/overview.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})
