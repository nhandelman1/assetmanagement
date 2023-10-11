from django.contrib import admin


class SolarBillDataAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Basic Information", {"fields": ["real_estate", "service_provider", "notes", "bill_file"]}),
        ("Date Information", {"fields": ["start_date", "end_date", "paid_date"]}),
        ("Cost Information", {"fields": ["actual_costs", "total_cost", "tax_rel_cost"]}),
        ("Total Usage Information", {"fields": ["solar_kwh", "home_kwh"]}),
        ("Opportunity Cost Information", {"fields": ["oc_bom_basis", "oc_pnl_pct", "oc_pnl", "oc_eom_basis"]})]
    list_display = ["service_provider", "real_estate", "start_date", "end_date", "paid_date", "total_cost"]
    list_filter = ["service_provider", "real_estate", "start_date", "end_date", "paid_date"]
    search_fields = ["notes"]
