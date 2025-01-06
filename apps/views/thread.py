import datetime

from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, ListView

from apps.forms import ThreatForm
from apps.models import Thread, Order


class ThreatListFormView(FormView):
    form_class = ThreatForm
    template_name = 'apps/site/threat-list.html'
    success_url = reverse_lazy('threat')

    def form_valid(self, form):
        data = form.cleaned_data
        if data.get('discount_price') > data.get('product').salasman_price:
            messages.error(self.request, 'Discount price must be greater than salasman.')
            return redirect('market')
        data['owner'] = self.request.user
        Thread.objects.create(**data)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['threats'] = self.request.user.threads.order_by('-create_at')
        return context


class StatistikaListView(ListView):
    queryset = Thread.objects.all()
    template_name = 'apps/salesman/statistika.html'
    context_object_name = 'statics'


    def get_queryset(self):
        query = super().get_queryset()
        if period:=self.request.GET.get('period'):
            today = timezone.now().date()
            time_dict = {
                'today': (today, today),
                'last_day': (today-datetime.timedelta(days=1), today-datetime.timedelta(days=1)),
                'wekly':(today-datetime.timedelta(days=7),today),
                'monthly':(today - datetime.timedelta(days=30),today)
            }
            time_output=time_dict.get(period)
            query = query.filter(create_at__date__range=time_output)
        query = query.filter(owner_id=self.request.user).select_related('product').annotate(
            new=Count('order', filter=Q(order__status=Order.StatusType.NEW)),
            read_to_start=Count('order', filter=Q(order__status=Order.StatusType.READ_TO_START)),
            delivering=Count('order', filter=Q(order__status=Order.StatusType.DELIVERING)),
            delivered=Count('order', filter=Q(order__status=Order.StatusType.DELIVERED)),
            cancelled_call=Count('order', filter=Q(order__status=Order.StatusType.CANCELED_CALL)),
            cancelled=Count('order', filter=Q(order__status=Order.StatusType.CANCELLED)),
            archived=Count('order', filter=Q(order__status=Order.StatusType.ARCHIVED)),
            visit_count=Count('visits')
        ).values(
            'title',
            'visit_count',
            'product__name',
            'new',
            'read_to_start',
            'delivering',
            'delivered',
            'cancelled_call',
            'cancelled',
            'archived'
        )
        return query


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        aggregated_data = self.get_queryset().aggregate(
            all_visit_count=Sum('visit_count'),
            all_new=Sum('new'),
            all_read_to_start=Sum('read_to_start'),
            all_delivering=Sum('delivering'),
            all_delivered=Sum('delivered'),
            all_cancelled_call=Sum('cancelled_call'),
            all_cancelled=Sum('cancelled'),
            all_archived=Sum('archived'),
        )
        context.update(aggregated_data)
        return context
