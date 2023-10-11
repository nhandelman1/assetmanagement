from django.contrib import admin


class DepreciationBillDataAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Basic Information", {"fields": ["real_estate", "service_provider", "real_property_value", "notes",
                                          "bill_file"]}),
        ("Date Information", {"fields": ["start_date", "end_date", "paid_date"]}),
        ("Cost Information", {"fields": ["period_usage_pct", "total_cost", "tax_rel_cost"]})]
    list_display = ["get_item", "real_estate", "service_provider", "start_date", "end_date", "paid_date", "total_cost"]
    list_filter = ["real_property_value__item", "start_date", "end_date", "paid_date"]
    search_fields = ["real_property_value__item", "notes"]

    @admin.display(ordering='real_property_value__item', description='Item')
    def get_item(self, bill_data):
        return bill_data.real_property_value.item
