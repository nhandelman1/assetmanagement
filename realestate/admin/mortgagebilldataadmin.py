from django.contrib import admin


class MortgageBillDataAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Basic Information", {"fields": ["real_estate", "service_provider", "notes", "bill_file"]}),
        ("Date Information", {"fields": ["start_date", "end_date", "paid_date"]}),
        ("Cost Information", {"fields": ["total_cost", "tax_rel_cost"]}),
        ("Mortgage Information", {"fields": ["outs_prin", "esc_bal", "prin_pmt", "int_pmt", "esc_pmt", "other_pmt"]})]
    list_display = ["service_provider", "real_estate", "start_date", "end_date", "paid_date", "total_cost"]
    list_filter = ["service_provider", "real_estate", "start_date", "end_date", "paid_date"]
    search_fields = ["notes"]
