from django.urls import path
from .views import (
    HomeView, CoursesView, FacultyView, ReviewsListView, ContactView,
    panel_login, panel_logout, panel_dashboard,
    panel_reviews, panel_approve_review, panel_reject_review,
    panel_inquiries, panel_mark_inquiry_read,
)

urlpatterns = [
    # ─── Public Pages ───
    path('', HomeView.as_view(), name='home'),
    path('courses/', CoursesView.as_view(), name='courses'),
    path('faculty/', FacultyView.as_view(), name='faculty'),
    path('reviews/', ReviewsListView.as_view(), name='reviews_page'),
    path('contact/', ContactView.as_view(), name='contact'),

    # ─── Custom Admin Panel ───
    path('panel/login/', panel_login, name='panel_login'),
    path('panel/logout/', panel_logout, name='panel_logout'),
    path('panel/', panel_dashboard, name='panel_dashboard'),
    path('panel/reviews/', panel_reviews, name='panel_reviews'),
    path('panel/reviews/<int:review_id>/approve/', panel_approve_review, name='panel_approve_review'),
    path('panel/reviews/<int:review_id>/reject/', panel_reject_review, name='panel_reject_review'),
    path('panel/inquiries/', panel_inquiries, name='panel_inquiries'),
    path('panel/inquiries/<int:inquiry_id>/read/', panel_mark_inquiry_read, name='panel_mark_inquiry_read'),
]
