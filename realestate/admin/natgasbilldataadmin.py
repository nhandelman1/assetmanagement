from django.contrib import admin


class NatGasBillDataAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Basic Information", {"fields": ["real_estate", "service_provider", "is_actual", "notes", "bill_file"]}),
        ("Date Information", {"fields": ["start_date", "end_date", "paid_date"]}),
        ("Total Cost Information", {"fields": ["total_cost", "tax_rel_cost"]}),
        ("Total Usage Information", {"fields": ["total_therms", "saved_therms"]}),
        ("Delivery Service Cost Information",
         {"fields": ["bsc_therms", "bsc_cost", "next_therms", "next_rate", "next_cost", "over_therms", "over_rate",
                     "over_cost", "dra_rate", "dra_cost", "sbc_rate", "sbc_cost", "tac_rate", "tac_cost", "bc_cost",
                     "ds_nysls_rate", "ds_nysls_cost", "ds_nysst_rate", "ds_nysst_cost", "ds_total_cost"]}),
        ("Supply Service Cost Information",
         {"fields": ["gs_rate", "gs_cost", "ss_nysls_rate", "ss_nysls_cost", "ss_nysst_rate", "ss_nysst_cost",
                     "ss_total_cost"]}),
        ("Other Charges/Adjustments Cost Information", {"fields": ["pbc_cost", "oca_total_cost"]})]
    list_display = ["service_provider", "real_estate", "start_date", "end_date", "paid_date", "total_cost", "is_actual"]
    list_filter = ["service_provider", "real_estate", "start_date", "end_date", "paid_date", "is_actual"]
    search_fields = ["notes"]
