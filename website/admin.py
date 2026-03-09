from django.contrib import admin
from .models import Inquiry


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'course', 'submitted_at', 'is_read')
    list_filter = ('course', 'is_read', 'submitted_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('submitted_at',)
    list_editable = ('is_read',)
    ordering = ('-submitted_at',)

    def get_course_display(self, obj):
        return obj.get_course_display()
    get_course_display.short_description = 'Course'
