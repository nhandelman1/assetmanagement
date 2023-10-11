from django.contrib import admin


class ElectricDataAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Basic Information", {"fields": ["real_estate", "service_provider"]}),
        ("Date Information", {"fields": ["month_date", "year_month"]}),
        ("Delivery Service Cost Information", {"fields": ["first_kwh", "first_rate", "next_rate", "mfc_rate"]}),
        ("Power Supply Cost Information", {"fields": ["psc_rate"]}),
        ("Taxes and Other Cost Information",
         {"fields": ["der_rate", "dsa_rate", "rda_rate", "nysa_rate", "rbp_rate", "spta_rate"]})]
    list_display = ["service_provider", "real_estate", "year_month"]
    list_filter = ["service_provider", "real_estate", "month_date"]
