from django.contrib import admin
from django.utils.html import format_html

from apps.models import Category, Product, AdminSite, User, WithDraw


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','phone', 'role','email', 'full_name','balance')
    list_editable = 'role',
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full name'
    def phone(self, obj):
        return f"+998 {obj.phone_number}"
    phone.short_description = 'Phone Number'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    exclude = ['slug']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    exclude = ['slug']


@admin.register(AdminSite)
class AdminSite(admin.ModelAdmin):
    pass

@admin.register(WithDraw)
class WithDrawAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone_number','status_button','status', 'cart_number', 'formatted_create_at', 'image_format',
                    'image')
    list_editable = 'status','image',

    def formatted_create_at(self, obj):
        return obj.create_at.strftime('%Y-%m-%d %H:%M:%S')

    formatted_create_at.short_description = "Created at"

    def phone_number(self, obj):
        return f"+998 {obj.user.phone_number}"

    phone_number.short_description = "User phone number"

    def image_format(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:30px;height:30px;"/>', obj.image.url)
        return '-'

    image_format.short_description = "Image"

    def status_button(self, obj):
        if obj.status == "under review":
            color = 'blue'
        elif obj.status == "completed":
            color = 'green'
        elif obj.status == "canceled":
            color = 'red'
        else:
            color = 'gray'
        return format_html(
            '<button style="background-color: {}; color: white; border: none; padding: 5px 10px;">{}</button>',
            color,
            obj.status.capitalize(),
        )

    status_button.short_description = "Status"

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = WithDraw.objects.get(id=obj.id)
            if old_obj.status != "canceled" and obj.status == "canceled":
                self.return_funds(obj,obj.user)
        super().save_model(request, obj, form, change)

    def return_funds(self, obj,user):
        User.objects.filter(id=user.id).update(balance=user.balance + obj.amount)
