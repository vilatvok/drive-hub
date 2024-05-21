from django.contrib import admin

from enterprises.models import Company, CarService


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'is_verified']
    list_display_links = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CarService)
class CarServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'owner', 'industry', 'is_verified']
    list_display_links = ['name']
    list_filter = ['industry']
    prepopulated_fields = {'slug': ('name',)}
