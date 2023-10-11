from django.contrib import admin


class EstimateNoteAdmin(admin.ModelAdmin):
    list_display = ["note_type", "real_estate", "service_provider", "note_order"]
    list_filter = ["real_estate", "service_provider"]
