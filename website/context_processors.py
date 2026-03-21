from .models import SiteImage, CourseImage

def site_images(request):
    """
    Exposes all SiteImages and CourseImages to templates via dictionaries.
    Usage: {{ site_images.logo.url }}  /  {{ course_images.digital_vlsi.url }}
    """
    images = {}
    courses = {}
    try:
        for img in SiteImage.objects.all():
            images[img.key] = img.image
    except Exception:
        pass
    try:
        for img in CourseImage.objects.all():
            courses[img.key] = img.image
    except Exception:
        pass
    return {'site_images': images, 'course_images': courses}
