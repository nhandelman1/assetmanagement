from django.contrib import admin


class ElectricBillDataAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Basic Information", {"fields": ["real_estate", "service_provider", "is_actual", "notes", "bill_file"]}),
        ("Date Information", {"fields": ["start_date", "end_date", "paid_date"]}),
        ("Total Cost Information", {"fields": ["total_cost", "tax_rel_cost"]}),
        ("Total Usage Information", {"fields": ["total_kwh", "eh_kwh", "bank_kwh"]}),
        ("Delivery Service Cost Information",
         {"fields": ["bs_rate", "bs_cost", "first_kwh", "first_rate", "first_cost", "next_kwh", "next_rate",
                     "next_cost", "cbc_rate", "cbc_cost", "mfc_rate", "mfc_cost", "dsc_total_cost"]}),
        ("Power Supply Cost Information", {"fields": ["psc_rate", "psc_cost", "psc_total_cost"]}),
        ("Taxes and Other Cost Information",
         {"fields": ["der_rate", "der_cost", "dsa_rate", "dsa_cost", "rda_rate", "rda_cost", "nysa_rate", "nysa_cost",
                     "rbp_rate", "rbp_cost", "spta_rate", "spta_cost", "st_rate", "st_cost", "toc_total_cost"]})]
    list_display = ["service_provider", "real_estate", "start_date", "end_date", "paid_date", "total_cost", "is_actual"]
    list_filter = ["service_provider", "real_estate", "start_date", "end_date", "paid_date", "is_actual"]
    search_fields = ["notes"]



