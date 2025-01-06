from django.shortcuts import render
from django.views.generic import FormView, ListView

from apps.forms import OrderForm
from apps.models import Product, AdminSite, Order, Thread, Visit


class OrderDetailFormView(ListView, FormView):
    form_class = OrderForm
    queryset = Product.objects.all()
    context_object_name = 'product'
    template_name = 'apps/site/product-detail.html'

    def get_queryset(self):
        query = super().get_queryset()
        threat_id = self.kwargs.get('threat_id')
        if threat_id:
            thread = Thread.objects.filter(pk=threat_id).first()
            Visit.objects.create(thread=thread)
            product = thread.product
            query = query.filter(id=product.id).first()
            return query
        else:
            slug = self.kwargs.get('slug')
            query = Product.objects.filter(slug=slug).first()
            return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site'] = AdminSite.objects.first()
        threat_id = self.kwargs.get('threat_id')
        context['all_amount'] = context['product'].discount_price
        if threat_id:
            context['thread'] = Thread.objects.filter(pk=threat_id).first()
            context['all_amount'] -= context['thread'].discount_price
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        site = AdminSite.objects.first()
        product = Product.objects.filter(slug=data.get('product')).first()
        product.quantity -= 1
        product.save()
        data['product'] = product
        data['user'] = self.request.user
        product_price = product.discount_price
        if data['thread']:
            thread = Thread.objects.filter(pk=data['thread']).first()
            data['thread'] = thread
            product_price -= thread.discount_price
        else:
            del data['thread']
        all_amount = product_price + site.delivery_price
        data['all_amount'] = all_amount
        obj, created = Order.objects.get_or_create(**data)
        context = {
            'order': obj,
            'site': site,
            'product_price': product_price,

        }

        return render(self.request, 'apps/order/success.html', context)


class OrderListView(ListView):
    queryset = Order.objects.select_related('district').all()
    template_name = 'apps/order/order-list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(user=self.request.user).all()
        return query
