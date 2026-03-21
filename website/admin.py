from django.contrib import admin
from .models import Inquiry, Review, SiteImage, CourseImage


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

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'rating', 'is_approved', 'submitted_at')
    list_filter = ('course', 'rating', 'is_approved')
    search_fields = ('name', 'email', 'text')
    list_editable = ('is_approved',)
    readonly_fields = ('submitted_at',)

@admin.register(SiteImage)
class SiteImageAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')
    search_fields = ('key', 'description')

@admin.register(CourseImage)
class CourseImageAdmin(admin.ModelAdmin):
    list_display = ('key', 'description')
    search_fields = ('key', 'description')
