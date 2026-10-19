# Register your models here.
from django.contrib import admin

from .models import Category, Customer, Order, OrderItem, Payment, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)
    list_select_related = ()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "stock", "is_active")
    search_fields = ("name", "sku", "category__name")
    list_filter = ("category", "is_active")
    list_select_related = ("category",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "created_at")
    search_fields = ("user__username", "user__email")
    list_select_related = ("user",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "customer", "status", "created_at")
    search_fields = (
        "reference",
        "customer__user__username",
        "customer__user__email",
    )
    list_filter = ("status", "created_at")
    list_select_related = ("customer__user",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "unit_price")
    search_fields = ("order__reference", "product__name", "product__sku")
    list_select_related = ("order", "product")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "status", "provider", "created_at")
    search_fields = ("order__reference", "transaction_reference")
    list_filter = ("status", "provider")
    list_select_related = ("order",)