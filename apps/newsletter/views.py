from django.shortcuts import redirect, render
from django.views import View
from .models import NewsletterSubscriber

class SubscribeView(View):
    template_name = 'newsletter/subscribe.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        if email:
            NewsletterSubscriber.objects.get_or_create(email=email)
        return redirect('newsletter:thanks')
