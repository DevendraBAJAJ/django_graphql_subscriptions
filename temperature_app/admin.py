from django.contrib import admin

# Register your models here.
from temperature_app.models import Temperature


@admin.register(Temperature)
class TemperatureAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'value', 'unit']
