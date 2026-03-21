from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import threading
from .models import Inquiry, Review

def send_email_async(subject, plain_message, html_message):
    def send():
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email='Ankira Solutions <bkiranbabuu2023@gmail.com>',
                recipient_list=['ankirasolutions@gmail.com'],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email: {e}")
    threading.Thread(target=send).start()


# ─────────────────────────────────────────────
#  PUBLIC SITE VIEWS
# ─────────────────────────────────────────────

class HomeView(View):
    template_name = 'home.html'

    def get(self, request):
        approved_reviews = Review.objects.filter(is_approved=True).order_by('-submitted_at')[:3]
        return render(request, self.template_name, {'approved_reviews': approved_reviews})

    def post(self, request):
        """Handle review submission from homepage form."""
        name = request.POST.get('reviewer_name', '').strip()
        email = request.POST.get('reviewer_email', '').strip()
        course = request.POST.get('reviewer_course', '').strip()
        rating = request.POST.get('reviewer_rating', '5').strip()
        text = request.POST.get('reviewer_text', '').strip()

        review_error = None
        review_success = False

        if not name or not text:
            review_error = 'Name and review text are required.'
        elif len(text) < 20:
            review_error = 'Please write at least 20 characters for your review.'
        else:
            try:
                Review.objects.create(
                    name=name,
                    email=email,
                    course=course,
                    rating=int(rating) if rating.isdigit() and 1 <= int(rating) <= 5 else 5,
                    text=text,
                    is_approved=False,
                )
                review_success = True
                
                # Send email notification asynchronously
                html_message = render_to_string('emails/new_review.html', {
                    'name': name, 'email': email, 'course': course,
                    'rating': rating, 'text': text
                })
                plain_message = strip_tags(html_message)
                send_email_async('New Review Pending Approval - Ankira Solutions', plain_message, html_message)
                
            except Exception:
                review_error = 'Something went wrong. Please try again.'

        approved_reviews = Review.objects.filter(is_approved=True).order_by('-submitted_at')[:6]
        return render(request, self.template_name, {
            'approved_reviews': approved_reviews,
            'review_success': review_success,
            'review_error': review_error,
        })


class CoursesView(TemplateView):
    template_name = 'courses.html'


class FacultyView(TemplateView):
    template_name = 'faculty_placement.html'


class ReviewsListView(View):
    """Public page showing all approved reviews."""
    template_name = 'reviews.html'

    def get(self, request):
        reviews = Review.objects.filter(is_approved=True).order_by('-submitted_at')
        total = reviews.count()
        # Compute average rating
        if total:
            avg = sum(r.rating for r in reviews) / total
        else:
            avg = 0
        return render(request, self.template_name, {
            'reviews': reviews,
            'total_reviews': total,
            'avg_rating': avg,
            'avg_rating_int': round(avg),
        })


class ContactView(View):
    template_name = 'contact.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        course = request.POST.get('course', '').strip()
        message = request.POST.get('message', '').strip()

        form_errors = {}
        form_data = {'name': name, 'phone': phone, 'email': email,
                     'course': course, 'message': message}

        if not name:
            form_errors['name'] = 'Full name is required.'
        elif len(name) < 2:
            form_errors['name'] = 'Please enter a valid name.'

        if not phone:
            form_errors['phone'] = 'Phone number is required.'
        elif len(phone) < 7:
            form_errors['phone'] = 'Please enter a valid phone number.'

        if not email:
            form_errors['email'] = 'Email address is required.'
        elif '@' not in email or '.' not in email:
            form_errors['email'] = 'Please enter a valid email address.'

        if form_errors:
            return render(request, self.template_name, {
                'form_errors': form_errors,
                'form_data': form_data,
                'error': True,
            })

        try:
            Inquiry.objects.create(
                name=name, phone=phone, email=email,
                course=course, message=message,
            )
            
            # Send email notification asynchronously
            html_message = render_to_string('emails/new_inquiry.html', {
                'name': name, 'phone': phone, 'email': email,
                'course': course, 'message': message
            })
            plain_message = strip_tags(html_message)
            send_email_async('New Inquiry Received - Ankira Solutions', plain_message, html_message)
            
            return render(request, self.template_name, {'success': True})
        except Exception:
            return render(request, self.template_name, {
                'form_data': form_data, 'error': True,
            })


# ─────────────────────────────────────────────
#  CUSTOM ADMIN PANEL VIEWS
# ─────────────────────────────────────────────

def panel_login(request):
    """Custom admin panel login."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('panel_dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('panel_dashboard')
        else:
            error = 'Invalid credentials or insufficient permissions.'

    return render(request, 'panel/login.html', {'error': error})


def panel_logout(request):
    """Log out and redirect to panel login."""
    logout(request)
    return redirect('panel_login')


@login_required(login_url='/panel/login/')
def panel_dashboard(request):
    """Admin dashboard with overview stats."""
    if not request.user.is_staff:
        return redirect('panel_login')

    pending_count = Review.objects.filter(is_approved=False).count()
    unread_count = Inquiry.objects.filter(is_read=False).count()

    stats = {
        'pending_reviews': pending_count,
        'approved_reviews': Review.objects.filter(is_approved=True).count(),
        'total_reviews': Review.objects.count(),
        'unread_inquiries': unread_count,
        'total_inquiries': Inquiry.objects.count(),
    }
    recent_inquiries = Inquiry.objects.filter(is_read=False).order_by('-submitted_at')[:5]
    pending_reviews = Review.objects.filter(is_approved=False).order_by('-submitted_at')[:5]

    return render(request, 'panel/dashboard.html', {
        'pending_reviews_count': pending_count,
        'unread_inquiries_count': unread_count,
        'stats': stats,
        'recent_inquiries': recent_inquiries,
        'pending_reviews': pending_reviews,
    })


@login_required(login_url='/panel/login/')
def panel_reviews(request):
    """List all reviews with approve / reject actions."""
    if not request.user.is_staff:
        return redirect('panel_login')

    status_filter = request.GET.get('status', 'pending')  # Default to pending
    reviews = Review.objects.all()
    if status_filter == 'pending':
        reviews = reviews.filter(is_approved=False)
    elif status_filter == 'approved':
        reviews = reviews.filter(is_approved=True)

    pending_count = Review.objects.filter(is_approved=False).count()
    approved_count = Review.objects.filter(is_approved=True).count()

    return render(request, 'panel/reviews.html', {
        'reviews': reviews,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'pending_reviews_count': pending_count,
        'unread_inquiries_count': Inquiry.objects.filter(is_read=False).count(),
    })


@login_required(login_url='/panel/login/')
def panel_approve_review(request, review_id):
    """Approve a review — redirect to pending list so the approved review disappears from view."""
    if not request.user.is_staff:
        return redirect('panel_login')
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id)
        review.is_approved = True
        review.save()
    # Always redirect to pending filter: approved review won't be in this list
    from django.urls import reverse
    return redirect(reverse('panel_reviews') + '?status=pending')


@login_required(login_url='/panel/login/')
def panel_reject_review(request, review_id):
    """Permanently delete a review — redirect to pending list."""
    if not request.user.is_staff:
        return redirect('panel_login')
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id)
        review.delete()
    # Always redirect to pending filter: deleted review won't be in any list
    from django.urls import reverse
    return redirect(reverse('panel_reviews') + '?status=pending')


@login_required(login_url='/panel/login/')
def panel_inquiries(request):
    """List all inquiries."""
    if not request.user.is_staff:
        return redirect('panel_login')

    status_filter = request.GET.get('status', 'unread')  # Default to unread
    inquiries = Inquiry.objects.all()
    if status_filter == 'unread':
        inquiries = inquiries.filter(is_read=False)
    elif status_filter == 'read':
        inquiries = inquiries.filter(is_read=True)

    unread_count = Inquiry.objects.filter(is_read=False).count()
    read_count = Inquiry.objects.filter(is_read=True).count()

    return render(request, 'panel/inquiries.html', {
        'inquiries': inquiries,
        'status_filter': status_filter,
        'unread_count': unread_count,
        'read_count': read_count,
        'pending_reviews_count': Review.objects.filter(is_approved=False).count(),
        'unread_inquiries_count': unread_count,
    })


@login_required(login_url='/panel/login/')
def panel_mark_inquiry_read(request, inquiry_id):
    """Mark an inquiry as read — redirect to unread filter so it disappears from view."""
    if not request.user.is_staff:
        return redirect('panel_login')
    if request.method == 'POST':
        inquiry = get_object_or_404(Inquiry, id=inquiry_id)
        inquiry.is_read = True
        inquiry.save()
    # Redirect to unread filter: the read inquiry won't appear there
    from django.urls import reverse
    return redirect(reverse('panel_inquiries') + '?status=unread')
