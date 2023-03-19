from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
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


class AddressListView(ListView):
    model = models.Address

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = models.Address
    fields = [
        'name',
        'address1',
        'address2',
        'zip_code',
        'city',
        'country',
    ]
    success_url = reverse_lazy('address_list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Address
    fields = [
        'name',
        'address1',
        'address2',
        'zip_code',
        'city',
        'country',
    ]
    success_url = reverse_lazy('address_list')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Address
    success_url = reverse_lazy('address_list')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
