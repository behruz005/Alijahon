from lib2to3.fixes.fix_input import context

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, DetailView

from apps.forms import SearchForm, OperatorForm
from apps.models import Order, Region, Category


class OperatorFormView(ListView, FormView):
    form_class = SearchForm
    queryset = Order.objects.all()
    template_name = 'apps/operator/operator-page.html'
    context_object_name = 'orders'
    success_url = 'operator'

    def get_queryset(self):
        status = self.request.GET.get('status')
        query = super().get_queryset()
        if status:
            query = query.filter(status=status)
        else:
            query = query.filter(status='new')
        return query

    def get_context_data(self, *args, **kwargs):
        context = {}
        if not kwargs.get('form'):
            context = super().get_context_data(*args, **kwargs)
        context['regions'] = Region.objects.all()
        context['categories'] = Category.objects.all()
        context['status'] = Order.StatusType
        if kwargs.get('form'):
            context['orders'] = Order.objects.filter(**kwargs.get("form").cleaned_data).all()
        return context

    def form_valid(self, form):
        self.context = self.get_context_data(form=form)
        return self.render_to_response(context)


class OperatorView(FormView, DetailView):
    queryset = Order.objects.all()
    form_class = OperatorForm
    pk_url_kwarg = 'pk'
    template_name = 'apps/operator/operator-detial.html'
    context_object_name = 'order'
    success_url = reverse_lazy('operator')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all()
        return context

    def form_valid(self, form):
        status = form.cleaned_data.get('status')
        query = Order.objects.filter(pk=self.kwargs.get('pk'))
        obj=query.first()
        if status == Order.StatusType.DELIVERED.value and obj.thread:
            thread = obj.thread
            user = thread.owner
            transfer_pay = obj.product.salasman_price - thread.discount_price
            user.balance+=transfer_pay
            user.save()
        query.update(**form.cleaned_data)
        return super().form_valid(form)
    def form_invalid(self, form):
        for error in form.errors:
            messages.error(self.request, f'{error.message}')
        return redirect('operator_detial',pk=self.kwargs.get('pk'))


