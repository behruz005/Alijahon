from lib2to3.fixes.fix_input import context

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.views import LogoutView
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from apps.forms import (AuthForm, ProfileForm,
                        NewPasswordForm, WithDrewForm)
from apps.models import User, WishList, Region, WithDraw


class AuthFormView(FormView):
    form_class = AuthForm
    template_name = 'apps/user/auth.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        phone_number = cleaned_data.get('phone_number')
        user: User = User.objects.filter(phone_number=phone_number).first()
        if not user:
            password = make_password(cleaned_data.get('password'))
            obj, created = User.objects.get_or_create(phone_number=phone_number, password=password)
            login(self.request, obj)
            return super().form_valid(form)
        else:
            if check_password(cleaned_data.get('password'), user.password):
                login(self.request, user)
                return super().form_valid(form)
            else:
                messages.error(self.request, 'Your password is incorrect.')
                return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid phone number.')
        return super().form_invalid(form)


class PasswordFormView(FormView):
    form_class = NewPasswordForm
    template_name = 'apps/user/profile.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = self.request.user
        if check_password(form.cleaned_data.get('old_password'), user.password):
            User.objects.filter(pk=self.request.user.pk).update(
                password=make_password(form.cleaned_data.get('new_password')))
            login(self.request, user)
            messages.success(self.request, 'Success change password.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Your password is incorrect.')
            login(self.request, user)
            return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "\n".join([i[0] for i in form.errors.values()]))
        return super().form_invalid(form)


class Logout(LogoutView):
    template_name = 'apps/site/main.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        User.objects.filter(phone_number=request.user.phone_number).delete()

        return redirect(self.success_url)


def wishlist(request):
    if request.POST:
        user = request.user
        if not user:
            return redirect('auth')

        product_id = request.POST.get('product_id')
        obj, created = WishList.objects.get_or_create(user_id=request.user.id, product_id=product_id)
        if not created:
            obj.delete()

        return JsonResponse({'response': created})
    else:
        context = {
            'wishlists': request.user.wishlists.all(),
        }
        return render(request, 'apps/site/wishlists.html', context)


class ProfileFormView(FormView):
    form_class = ProfileForm
    template_name = 'apps/user/profile.html'
    success_url = reverse_lazy('profile')
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all()
        return context

    def form_valid(self, form):
        user = self.request.user
        User.objects.filter(id=user.id).update(**form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


    def get_object(self, queryset=None):
        return self.request.user


class WithDrewFormView(FormView,ListView):
    queryset = WithDraw.objects.all()
    context_object_name = 'withdraws'
    form_class = WithDrewForm
    template_name = 'apps/user/withdraw.html'
    success_url = 'withdraw'
    def get_queryset(self):
        query=super().get_queryset()
        query=query.filter(user=self.request.user.pk)
        return query
    def form_valid(self, form):
        form_data = form.cleaned_data
        user:User=self.request.user
        if form_data.get('type') == 'money' and form_data.get('amount')>user.balance:
            messages.error(self.request, 'You cannot withdraw money.')
            return redirect('withdraw')
        elif form_data.get('type') == 'coin' and form_data.get('coin')<user.coin:
            messages.error(self.request, 'You cannot withdraw coin.')
            return redirect('withdraw')
        if form_data.get('type') == 'money' and form_data.get('amount')<=user.balance:
            user.balance -= form_data.get('amount')
        elif form_data.get('type') == 'coin' and form_data.get('coin')<=user.coin:
            user.coin += form_data.get('amount')
        user.save()
        form=form.save(commit=False)
        form.user = user
        form.save()
        return super().form_valid(form)
    def get_context_data(self,*args, **kwargs):
       context=super().get_context_data(*args,**kwargs)
       context.update(self.get_queryset().filter(status=WithDraw.WithDrawStatus.COMPLETED).aggregate(
           completed_pay=Sum('amount')
       ))
       return context


















