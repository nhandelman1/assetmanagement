from django.contrib import admin


class NatGasDataAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Basic Information", {"fields": ["real_estate", "service_provider"]}),
        ("Date Information", {"fields": ["month_date", "year_month"]}),
        ("Delivery Service Cost Information",
         {"fields": ["bsc_therms", "bsc_rate", "next_therms", "next_rate", "over_rate", "dra_rate", "wna_low_rate",
                     "wna_high_rate", "sbc_rate", "tac_rate", "bc_rate", "ds_nysls_rate", "ds_nysst_rate"]}),
        ("Supply Service Cost Information",
         {"fields": ["gs_rate", "ss_nysls_rate", "ss_nysst_rate"]}),
        ("Other Charges/Adjustments Cost Information", {"fields": ["pbc_rate"]})]
    list_display = ["real_estate", "service_provider", "year_month"]
    list_filter = ["service_provider", "real_estate", "month_date"]
