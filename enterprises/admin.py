from django.contrib import admin
from .models import Company, CarService

# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "is_verified"]
    list_display_links = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CarService)
class CarServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "company", "owner", "industry", "is_verified"]
    list_display_links = ["name"]
    list_filter = ["industry"]
    prepopulated_fields = {"slug": ("name",)}