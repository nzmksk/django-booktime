from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from main import forms, models
import logging

logger = logging.getLogger(__name__)


class SignUpView(FormView):
    template_name = 'signup.html'
    form_class = forms.UserCreationForm

    def get_success_url(self):
        redirect_to = self.request.GET.get('next', '/')
        return redirect_to

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        email = form.cleaned_data.get('email')
        raw_passward = form.cleaned_data.get('password1')

        logger.info('New signup for email=%s through SignUpView', email)

        user = authenticate(email=email, password=raw_passward)
        login(self.request, user)
        form.send_mail()
        messages.info(self.request, 'You signed up successfully.')

        return response


class ContactUsView(FormView):
    template_name = 'contact_form.html'
    form_class = forms.ContactForm
    success_url = '/'

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)


class ProductListView(ListView):
    template_name = 'product_list.html'
    paginate_by = 4

    def get_queryset(self):
        tag = self.kwargs['tag']
        self.tag = None
        if tag != 'all':
            self.tag = get_object_or_404(models.ProductTag, slug=tag)
        if self.tag:
            products = models.Product.objects.active().filter(tags=self.tag)
        else:
            products = models.Product.objects.active()

        return products.order_by('name')
