from django.urls import path

from apps.views import (AuthFormView, Logout, HomeListView, ProfileFormView,
                        get_district, PasswordFormView, CategoryListView,
                        wishlist, OrderDetailFormView, MarketListView,
                        OrderListView, CompetitionListView,
                        ThreatListFormView, StatistikaListView, OperatorFormView, OperatorView, WithDrewFormView)

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('category/<str:slug>', CategoryListView.as_view(), name='category'),
    path('product/<str:slug>', OrderDetailFormView.as_view(), name='product'),
]


urlpatterns += [
    path('auth', AuthFormView.as_view(), name='auth'),
    path('logout', Logout.as_view(), name='logout'),
    path('profile', ProfileFormView.as_view(), name='profile'),
    path('district', get_district, name='get_districts'),
    path('new-password', PasswordFormView.as_view(), name='new_password'),
    path('wishlist', wishlist, name='wishlist'),

]


urlpatterns += [
    path('market/<str:slug>', MarketListView.as_view(), name='market'),
    path('order-list', OrderListView.as_view(), name='order_list'),
    path('oqim', ThreatListFormView.as_view(), name='threat'),
    path('oqim/<int:threat_id>', OrderDetailFormView.as_view(), name='order_detail'),
    path('statistika', StatistikaListView.as_view(), name='statistika'),
]


urlpatterns += [
    path('operator', OperatorFormView.as_view(), name='operator'),
    path('opertator/detial/<int:pk>', OperatorView.as_view(), name='operator_detial'),
    path('competition', CompetitionListView.as_view(), name='competition'),
    path('withdraw', WithDrewFormView.as_view(), name='withdraw')
]
