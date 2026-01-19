from django.contrib import admin
from .models import Sign

@admin.register(Sign)
class SignAdmin(admin.ModelAdmin):
    list_display = ('word', 'get_filename', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('word',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Sign Information', {
            'fields': ('word', 'sigml_file')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_filename(self, obj):
        return obj.get_filename()
    get_filename.short_description = 'Filename'