from lib2to3.fixes.fix_input import context

from django.db.models import Sum, Count
from django.http import JsonResponse
from django.views.generic import ListView, TemplateView

from apps.models import District, Category, Product, AdminSite, Region, User, Thread, Order


class HomeListView(ListView):
    queryset = Category.objects.all()
    template_name = 'apps/site/main.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context




def get_district(request):
    region_id = request.GET.get('region_id')
    if region_id:
        districts = District.objects.filter(region_id=region_id).values('id', 'name')
        return JsonResponse(list(districts), safe=False)
    return JsonResponse({'error': 'No region selected'}, status=400)







class CategoryListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/site/category.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.kwargs.get('slug')
        if query in 'all':
            return Product.objects.all()
        return Product.objects.filter(category__slug=query).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['slug'] = self.kwargs.get('slug')
        return context





class MarketListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/site/market.html'
    context_object_name = 'products'

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        if slug in 'all':
            return Product.objects.all()
        elif slug in 'top':
            return Product.objects.annotate(total_sold=Sum('orders__quantity')).order_by('-total_sold')

        return Product.objects.filter(category__slug=slug).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['slug'] = self.kwargs.get('slug')
        context['site'] = AdminSite.objects.first()
        return context


class CompetitionListView(ListView):
    queryset = User.objects.all()
    template_name = 'apps/site/competition.html'
    context_object_name = 'users'

    def get_queryset(self):
        query = super().get_queryset()
        query = query.annotate(sold=Count('threads__order',
                                          threads__order__status=Order.StatusType.DELIVERED.value
                                          )).filter(sold__gt=0).order_by('sold')

        return query
    def get_context_data(self, *args,**kwargs):
        context=super().get_context_data(*args,**kwargs)
        context['site'] = AdminSite.objects.first()
        return context

