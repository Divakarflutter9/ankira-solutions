from django.db import models


class Inquiry(models.Model):
    COURSE_CHOICES = [
        ('frontend', 'VLSI Frontend Design (RTL & Verification)'),
        ('backend', 'VLSI Backend Physical Design'),
        ('sta', 'Static Timing Analysis (STA)'),
        ('analog', 'Analog & Mixed Signal'),
        ('demo', 'Book Free Demo Class'),
        ('general', 'General Inquiry'),
    ]

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    course = models.CharField(max_length=50, choices=COURSE_CHOICES, blank=True)
    message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Inquiry'
        verbose_name_plural = 'Inquiries'

    def __str__(self):
        return f"{self.name} — {self.email} ({self.get_course_display()})"


class Review(models.Model):
    COURSE_CHOICES = [
        ('frontend', 'VLSI Frontend Design'),
        ('backend', 'VLSI Backend Physical Design'),
        ('sta', 'Static Timing Analysis'),
        ('analog', 'Analog & Mixed Signal'),
        ('general', 'General'),
    ]

    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    course = models.CharField(max_length=50, choices=COURSE_CHOICES, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    text = models.TextField()
    is_approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"{self.name} — {self.rating}★ ({self.get_course_display()})"

    def stars_display(self):
        return '★' * self.rating + '☆' * (5 - self.rating)


class SiteImage(models.Model):
    IMAGE_KEYS = [
        ('logo', 'Main Logo (Navbar & Footer)'),
        ('hero_image', 'Hero Section Graphic (Homepage)'),
        ('hero_bg', 'Hero Section Background (Homepage)'),
        ('about_image', 'About Us Image (Homepage)'),
        ('cta_bg', 'Call To Action Background (Homepage)'),
    ]
    
    key = models.CharField(max_length=50, choices=IMAGE_KEYS, unique=True, help_text="Select where this image should appear.")
    image = models.ImageField(upload_to='site_images/')
    description = models.CharField(max_length=200, blank=True, help_text="Optional description for your own reference.")

    class Meta:
        verbose_name = 'Site Image'
        verbose_name_plural = 'Site Images'

    def __str__(self):
        return self.key


class CourseImage(models.Model):
    COURSE_KEYS = [
        ('digital_vlsi', 'Digital VLSI Design (Homepage Card)'),
        ('physical_design', 'Physical Design (Homepage Card)'),
        ('fpga_design', 'FPGA Design (Homepage Card)'),
        ('frontend_design', 'VLSI Frontend Design (Courses Page)'),
        ('backend_design', 'VLSI Backend Physical Design (Courses Page)'),
        ('sta', 'Static Timing Analysis (Courses Page)'),
        ('analog_mixed', 'Analog & Mixed Signal (Courses Page)'),
    ]

    key = models.CharField(max_length=50, choices=COURSE_KEYS, unique=True, help_text="Select which course this image belongs to.")
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=200, blank=True, help_text="Optional label for your reference.")

    class Meta:
        verbose_name = 'Course Image'
        verbose_name_plural = 'Course Images'

    def __str__(self):
        return self.get_key_display()
