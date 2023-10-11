from django.contrib import admin


class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ["provider", "tax_category"]
    list_filter = ["tax_category"]
    search_fields = ["provider"]
