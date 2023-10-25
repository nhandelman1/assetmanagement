from django.contrib import admin

from ..forms.modelforms import SecurityMasterAdminForm


class SecurityMasterAdmin(admin.ModelAdmin):
    form = SecurityMasterAdminForm

    list_display = ["ticker", "asset_class", "asset_subclass", "my_id"]
    list_filter = ["asset_class", "asset_subclass"]
    search_fields = ["ticker", "asset_class", "asset_subclass"]
