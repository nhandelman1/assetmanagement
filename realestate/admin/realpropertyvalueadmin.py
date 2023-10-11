from django.contrib import admin


class RealPropertyValueAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Basic Information", {"fields": ["real_estate", "item", "dep_class", "notes"]}),
        ("Date Information", {"fields": ["purchase_date", "disposal_date"]}),
        ("Cost Information", {"fields": ["cost_basis"]})]
    list_display = ["item", "real_estate", "purchase_date"]
    list_filter = ["real_estate", "purchase_date", "dep_class"]
    search_fields = ["item"]