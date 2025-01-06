import re

from django.core.exceptions import ValidationError
from django.forms import Form, CharField, BooleanField, ModelForm, IntegerField, DateTimeField

from apps.models import Thread, WithDraw


class AuthForm(Form):
    phone_number = CharField(max_length=20, required=True)
    password = CharField(max_length=255, required=True)
    is_doc_read = BooleanField(disabled=False, required=False)  # yoki default=False

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 5:
            raise ValidationError('Password must be at least 8 characters')
        return password

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        cleaned_phone_number = re.sub(r'\D', '', phone_number)[3:]
        return cleaned_phone_number


class ProfileForm(Form):
    first_name = CharField(max_length=20, required=False)
    last_name = CharField(max_length=20, required=False)
    telegram_id = CharField(max_length=255, required=False)
    dec = CharField(max_length=1000, required=False)
    district = CharField(max_length=1000, required=False)
    address = CharField(max_length=255, required=False)

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        return cleaned_data

    def clean_telegram_id(self):
        telegram_id = self.cleaned_data['telegram_id']
        if not telegram_id:
            return None
        return telegram_id


class NewPasswordForm(Form):
    old_password = CharField(max_length=255, required=True)
    new_password = CharField(max_length=255, required=True)
    confirm_password = CharField(max_length=255, required=True)

    def clean(self):
        cleaned_data = super().clean()
        new_password = self.cleaned_data['new_password']
        confirm_password = self.cleaned_data['confirm_password']
        if new_password != confirm_password:
            raise ValidationError('Passwords do not match')
        if len(new_password) < 5:
            raise ValidationError('Password must be at least 8 characters')
        del cleaned_data['confirm_password']
        return cleaned_data


class OrderForm(Form):
    phone_number = CharField(max_length=20, required=True)
    full_name = CharField(max_length=255, required=True)
    product = CharField(max_length=255, required=True)
    thread = CharField(max_length=255, required=False)

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        cleaned_phone_number = re.sub(r'\D', '', phone_number)[3:]
        return cleaned_phone_number


class ThreatForm(ModelForm):
    class Meta:
        model = Thread
        exclude = ['created_at', 'updated_at', 'visit_count', 'owner']

    def clean(self):
        return self.cleaned_data


class SearchForm(Form):
    product__category_id = IntegerField(required=False)
    district_id = CharField(max_length=20, required=False)
    status = CharField(max_length=20, required=False)

    def clean_product__category_id(self):
        category = self.cleaned_data['product__category_id']
        if category:
            return category

    def clean_district_id(self):
        district = self.cleaned_data['district_id']
        if district:
            return district

    def clean_status(self):
        status = self.cleaned_data['status']
        if status:
            return status

    def clean(self):
        data = self.cleaned_data
        filter_data = {}
        for key, value in data.items():
            if value != None:
                filter_data.update({key: value})
        return filter_data

class WithDrewForm(ModelForm):
    cart_number = CharField(max_length=20, required=True)
    class Meta:
        model = WithDraw
        exclude = ['created_at', 'updated_at','user','status','message']
    def clean_cart_number(self):
        cart_number = self.cleaned_data['cart_number']
        cleaned_cart_number = re.sub(r'\D', '', cart_number)
        return cleaned_cart_number

class OperatorForm(Form):
    quantity = IntegerField(required=False)
    send_order_date = DateTimeField(required=False)
    district = CharField(max_length=20, required=False)
    status = CharField(max_length=20, required=False)
    dictionary = CharField(max_length=1000, required=False)

    def clean(self):
        return self.cleaned_data
