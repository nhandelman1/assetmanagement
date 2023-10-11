from django.contrib import admin


class MySunpowerHourlyDataAdmin(admin.ModelAdmin):
    list_display = ["dt", "solar_kwh", "home_kwh"]
    list_filter = ["dt"]
    search_fields = ["dt"]
