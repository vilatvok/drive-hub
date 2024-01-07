from django.contrib import admin
from .models import Fuel, Order, Coupon


@admin.register(Fuel)
class FuelAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "coupon", "date_update"]
    list_display_links = ["name", "coupon"]
    list_filter = ["date_update"]
    actions = ["call_off_coupons"]
    prepopulated_fields = {"slug": ("name",)}

    @admin.action(description="Call off coupons")
    def call_off_coupons(self, request, queryset):
        queryset.update(coupon=False)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["owner", "fuel_type", "payment", "date"]
    list_display_links = ["owner", "fuel_type"]
    list_filter = ["owner", "date"]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["name", "discount", "date_start", "date_end"]
