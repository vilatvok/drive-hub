from django.contrib import admin

from .models import ElectricCar, Fine, FuelCar

# Register your models here.


@admin.register(FuelCar)
class FuelCarAdmin(admin.ModelAdmin):
    list_display = ["owner", "name", "year"]
    list_display_links = ["owner"]


@admin.register(ElectricCar)
class ElectricCarAdmin(admin.ModelAdmin):
    list_display = ["owner", "name", "year"]
    list_display_links = ["owner"]


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ["person", "car", "type_of_fine", "created_date"]
    list_display_links = ["person"]
    list_filter = ["type_of_fine"]
