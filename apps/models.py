from django.apps import apps
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes.models import ContentType

from django.db import models
from django.db.models import CharField, TextField, Model, OneToOneField, SET_NULL, ForeignKey, CASCADE, BooleanField, \
    ImageField, DecimalField, PositiveIntegerField, TextChoices, DateTimeField, DateField
from django.utils.text import slugify
from django.utils import timezone

# Create your models here.
class CustomUser(UserManager):
    def _create_user(self, phone_number, email, password, **extra_fields):

        if not phone_number:
            raise ValueError("The given phone number must be set")
        email = self.normalize_email(email)

        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        phone_number = GlobalUserModel.normalize_username(phone_number)
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, email, password, **extra_fields)

    def create_superuser(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, email, password, **extra_fields)


class BaseSlug(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            num = 1
            while self.__class__.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{num}'
                num += 1
            self.slug = unique_slug
        return super().save(*args, **kwargs)


class User(AbstractUser):
    class Roles(TextChoices):
        USER = 'user','User'
        ADMIN = 'admin','Admin'
        OPERATOR = 'operator','Operator'
        DELIVER = 'deliver','Deliver'

    role=CharField(max_length=50,choices=Roles.choices, default=Roles.USER)
    phone_number = CharField(max_length=9, unique=True, blank=True)
    district = OneToOneField('apps.District', SET_NULL, blank=True, null=True, related_name='district')
    telegram_id = CharField(max_length=255, unique=True, null=True, blank=True)
    dec = TextField(max_length=255, blank=True, null=True)
    address = CharField(max_length=255, null=True, blank=True)
    image = ImageField(upload_to="user/%y/%m/%d/", null=True, blank=True)
    is_doc_read = BooleanField(default=False, null=True, blank=True)
    USERNAME_FIELD = "phone_number"
    username = None
    objects = CustomUser()
    balance = DecimalField(max_digits=12,decimal_places=2,default=0)
    coin=PositiveIntegerField(default=0)
    threats = PositiveIntegerField(default=0)

    def __str__(self):
        return self.phone_number


    @property
    def wishlist_product(self):
        return self.wishlists.all().values_list('product', flat=True)


class Region(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class District(Model):
    name = CharField(max_length=255)
    region = ForeignKey('apps.Region', CASCADE, related_name='districts')

    def __str__(self):
        return self.name


class Category(BaseSlug):
    icon = CharField(max_length=255)

    def __str__(self):
        return self.name

class DateTimeBaseModel(Model):
    create_at = DateTimeField(auto_now_add=True)
    update_at = DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Product(BaseSlug,DateTimeBaseModel):
    image = ImageField(upload_to="product/")
    description = TextField(max_length=255, blank=True, null=True)
    price = DecimalField(max_digits=12, decimal_places=2)
    discount = DecimalField(max_digits=5, decimal_places=2, default=0)
    quantity = PositiveIntegerField(default=0)
    salasman_price = DecimalField(max_digits=12, decimal_places=2, default=0)
    category = ForeignKey('apps.Category', on_delete=CASCADE, related_name='products')

    @property
    def discount_price(self):
        return self.price * (100 - self.discount) / 100

    def __str__(self):
        return self.name


class WishList(DateTimeBaseModel):
    product = ForeignKey('apps.Product', on_delete=CASCADE, related_name='wishlists')
    user = ForeignKey('apps.User', on_delete=CASCADE, related_name='wishlists')

    def __str__(self):
        return self.user


class AdminSite(Model):
    delivery_price = DecimalField(max_digits=12, decimal_places=2, default=0)
    competition_photo = ImageField(upload_to="admin/", null=True, blank=True)
    competition_start = DateField(null=True, blank=True)
    competition_end = DateField(null=True, blank=True)
    message = TextField()

class Order(DateTimeBaseModel):
    class StatusType(TextChoices):
        NEW = 'new', 'New'
        READ_TO_START = 'read-to-start', 'Read-to-start'
        DELIVERING = 'delivering', 'Delivering'
        DELIVERED = 'delivered', 'Delivered'
        CANCELED_CALL = 'cancelled_call', 'Cancelled Call'
        CANCELLED = 'cancelled', 'Cancelled'
        ARCHIVED = 'archived', 'Archived'

    user = ForeignKey('apps.User', on_delete=CASCADE, related_name='orders')
    product = ForeignKey('apps.Product', on_delete=CASCADE, to_field='slug', related_name='orders')
    phone_number = CharField(max_length=12)
    full_name = CharField(max_length=255)
    quantity = PositiveIntegerField(default=1)
    status = CharField(max_length=20, choices=StatusType.choices, default=StatusType.NEW)
    thread = ForeignKey('apps.Thread',SET_NULL ,null=True,blank=True)
    district = ForeignKey('apps.District',SET_NULL,null=True,blank=True,related_name='orders')
    address = CharField(max_length=255)
    all_amount = DecimalField(max_digits=12, decimal_places=2, default=0)
    send_order_date = DateTimeField(default=timezone.now)
    dictionary = TextField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.product.discount_price
    @property
    def discount_price(self):
        amount=self.product.discount_price
        if self.thread:
            amount-=self.thread.discount_price
        return amount

class Thread(DateTimeBaseModel):
    owner = ForeignKey('apps.User', on_delete=CASCADE, related_name='threads')
    product = ForeignKey('apps.Product', on_delete=CASCADE, related_name='threads')
    title = CharField(max_length=255)
    discount_price = DecimalField(max_digits=12, decimal_places=2, default=0)
    create_at = DateTimeField(auto_now_add=True)

class Visit(DateTimeBaseModel):
    thread = ForeignKey('apps.Thread', on_delete=CASCADE, related_name='visits')

class WithDraw(DateTimeBaseModel):
    class WithDrawStatus(TextChoices):
        UNDER_REVIEW = 'under-review', 'Under-review'
        COMPLETED = 'completed', 'Completed'
        CANCELED = 'canceled', 'Canceled'
    class CashType(TextChoices):
        MONEY ='money','Money'
        COIN = 'coin' , 'Coin'

    user=ForeignKey('apps.User', on_delete=CASCADE, related_name='withdraws')
    cart_number = CharField(max_length=16)
    amount = DecimalField(max_digits=12, decimal_places=0)
    status = CharField(max_length=20, choices=WithDrawStatus.choices, default=WithDrawStatus.UNDER_REVIEW)
    type = CharField(max_length=20,choices=CashType.choices, default=CashType.MONEY)
    message = TextField(null=True, blank=True)
    image = ImageField(upload_to='withdraw/%Y/%m/%d/', null=True, blank=True)
    def __str__(self):
        return self.user.phone_number