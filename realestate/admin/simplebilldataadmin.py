from django.contrib import admin


class SimpleBillDataAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Basic Information", {"fields": ["real_estate", "service_provider", "notes", "bill_file"]}),
        ("Date Information", {"fields": ["start_date", "end_date", "paid_date"]}),
        ("Cost Information", {"fields": ["total_cost", "tax_rel_cost"]})]
    list_display = ["service_provider", "real_estate", "start_date", "end_date", "paid_date", "total_cost"]
    list_filter = ["service_provider", "real_estate", "start_date", "end_date", "paid_date"]
    search_fields = ["service_provider__provider", "service_provider__tax_category", "notes"]
