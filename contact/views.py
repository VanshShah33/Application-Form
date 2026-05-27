from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Count
from django.utils import timezone
import csv

from .models import Contact

# ── 1. HOMEPAGE: APPLICATION INTAKE ──
def home(request):
    # If the user is logged in, redirect them to portal if they already applied
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('dashboard')
        existing = Contact.objects.filter(user=request.user).first() or Contact.objects.filter(useremail=request.user.email).first()
        if existing:
            # Sync user model link if not set
            if not existing.user:
                existing.user = request.user
                existing.save()
            return redirect('student_portal')

    if request.method == 'POST':
        username = request.POST.get('username')
        useremail = request.POST.get('useremail')
        userphone = request.POST.get('userphone')
        userdob = request.POST.get('userdob')
        usergender = request.POST.get('usergender')
        usercity = request.POST.get('usercity')
        userstate = request.POST.get('userstate')
        usermessage = request.POST.get('usermessage')
        user_resume = request.FILES.get('user_resume')
        
        # Determine cohort interest from checked boxes
        interests = request.POST.getlist('interest')
        # We can append it to the message or store in status. Let's record interests.
        interest_text = ", ".join(interests) if interests else "General"
        usermessage = f"[Cohort Interests: {interest_text}]\n\n{usermessage}"

        contact = Contact.objects.create(
            username=username,
            useremail=useremail,
            userphone=userphone,
            userdob=userdob,
            usergender=usergender,
            usercity=usercity,
            userstate=userstate,
            usermessage=usermessage,
            user_resume=user_resume,
            # Link current user account if submitted while authenticated
            user=request.user if request.user.is_authenticated else None
        )
        
        # Link user if registration email matches
        if not contact.user:
            matching_user = User.objects.filter(email=useremail).first()
            if matching_user:
                contact.user = matching_user
                contact.save()

        # Send receipt email logged directly in terminal
        try:
            send_mail(
                subject='Scholarship Application Received! | She Can Foundation',
                message=f"Dear {username},\n\nThank you for applying to the She Can Foundation scholarship programs. We have securely logged your profile and interests.\n\nNext Steps:\n1. Admissions Review (2-4 business days)\n2. Virtual Chat Dialogue\n3. Cohort Alignment\n\nYou can sign up on our website using your email '{useremail}' to track your live review status!\n\nBest Regards,\nAdmissions Team\nShe Can Foundation",
                from_email='admissions@shecanfoundation.org',
                recipient_list=[useremail],
                fail_silently=True
            )
        except Exception:
            pass

        return render(request, 'success.html')
    
    return render(request, 'home.html')


# ── 2. STUDENT AUTHENTICATION VIEWS ──

def student_register(request):
    if request.user.is_authenticated:
        return redirect('student_portal')
        
    if request.method == 'POST':
        name = request.POST.get('username')
        email = request.POST.get('useremail')
        passw = request.POST.get('password')
        
        if not email or not passw:
            messages.error(request, "Please fill in all credentials.")
            return render(request, 'student_register.html')
            
        # Check if username or email already exists
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'student_register.html')
            
        # Create User
        user = User.objects.create_user(username=email, email=email, password=passw)
        user.first_name = name
        user.save()
        
        # Sync User Link in any pre-existing Contact forms
        contact = Contact.objects.filter(useremail=email).first()
        if contact:
            contact.user = user
            contact.save()
            
        # Log User In
        login(request, user)
        messages.success(request, "Registration successful!")
        return redirect('student_portal')
        
    return render(request, 'student_register.html')


def student_login(request):
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    is_admin_login = '/dashboard/' in next_url
    
    if request.user.is_authenticated:
        if next_url:
            return redirect(next_url)
        if request.user.is_superuser:
            return redirect('dashboard')
        return redirect('student_portal')
        
    if request.method == 'POST':
        email = request.POST.get('useremail')
        passw = request.POST.get('password')
        
        user = authenticate(request, username=email, password=passw)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            if next_url:
                return redirect(next_url)
            if user.is_superuser:
                return redirect('dashboard')
            return redirect('student_portal')
        else:
            messages.error(request, "Invalid email or password.")
            
    context = {
        'is_admin_login': is_admin_login,
        'next': next_url,
    }
    return render(request, 'student_login.html', context)


def student_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('student_login')


@login_required(login_url='student_login')
def student_portal(request):
    # Find matching applicant application
    contact = Contact.objects.filter(user=request.user).first() or Contact.objects.filter(useremail=request.user.email).first()
    
    # Associate user link if not set
    if contact and not contact.user:
        contact.user = request.user
        contact.save()
        
    context = {
        'contact': contact
    }
    return render(request, 'student_portal.html', context)


# ── 3. ADMINISTRATIVE ACTIONS & CSV EXPORT ──

@login_required(login_url='student_login')
def admin_toggle_verify(request, contact_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    contact = get_object_or_404(Contact, id=contact_id)
    contact.is_verified = not contact.is_verified
    contact.save()
    
    return JsonResponse({
        'success': True,
        'is_verified': contact.is_verified
    })


@login_required(login_url='student_login')
def admin_update_status(request, contact_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        status_val = request.POST.get('status')
        if status_val in ['Pending', 'Approved', 'Rejected']:
            contact = get_object_or_404(Contact, id=contact_id)
            contact.status = status_val
            
            # Automatically verify if approved
            if status_val == 'Approved':
                contact.is_verified = True
                
            contact.save()
            
            # Send status update email log
            try:
                send_mail(
                    subject='Application Status Update | She Can Foundation',
                    message=f"Dear {contact.username},\n\nYour scholarship application status has been updated to '{status_val}'.\n\nPlease log in to your Student Portal to check details and see the latest updates.\n\nBest Regards,\nShe Can Foundation Team",
                    from_email='admissions@shecanfoundation.org',
                    recipient_list=[contact.useremail],
                    fail_silently=True
                )
            except Exception:
                pass
                
            return JsonResponse({
                'success': True,
                'status': contact.status,
                'is_verified': contact.is_verified
            })
            
    return JsonResponse({'error': 'Invalid Request'}, status=400)


@login_required(login_url='student_login')
def admin_assign_cohort(request, contact_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        cohort_val = request.POST.get('cohort')
        contact = get_object_or_404(Contact, id=contact_id)
        contact.assigned_cohort = cohort_val
        contact.save()
        
        # Send cohort invitation email log
        try:
            send_mail(
                subject='Welcome to your Cohort! | She Can Foundation',
                message=f"Dear {contact.username},\n\nCongratulations! You have been successfully assigned to our specialized training track: '{cohort_val}'.\n\nYour assigned mentor will reach out in the next 48 hours with syllabus materials and study rings details.\n\nLog in to your Student Portal to view resources.\n\nBest Regards,\nShe Can Foundation Team",
                from_email='admissions@shecanfoundation.org',
                recipient_list=[contact.useremail],
                fail_silently=True
            )
        except Exception:
            pass
            
        return JsonResponse({
            'success': True,
            'assigned_cohort': contact.assigned_cohort
        })
        
    return JsonResponse({'error': 'Invalid Request'}, status=400)


@login_required(login_url='student_login')
def admin_save_applicant(request, contact_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        is_verified_str = request.POST.get('is_verified')
        # Handle string or boolean representation
        is_verified = is_verified_str == 'true' or is_verified_str == 'True'
        status_val = request.POST.get('status')
        cohort_val = request.POST.get('cohort')
        
        contact = get_object_or_404(Contact, id=contact_id)
        
        # Track changes to conditionally send emails
        status_changed = contact.status != status_val
        cohort_changed = contact.assigned_cohort != cohort_val
        
        contact.is_verified = is_verified
        if status_val in ['Pending', 'Approved', 'Rejected']:
            contact.status = status_val
            # Automatically verify if approved
            if status_val == 'Approved':
                contact.is_verified = True
                
        contact.assigned_cohort = cohort_val if cohort_val else None
        contact.save()
        
        # Send status update email if changed
        if status_changed:
            try:
                send_mail(
                    subject='Application Status Update | She Can Foundation',
                    message=f"Dear {contact.username},\n\nYour scholarship application status has been updated to '{status_val}'.\n\nPlease log in to your Student Portal to check details and see the latest updates.\n\nBest Regards,\nShe Can Foundation Team",
                    from_email='admissions@shecanfoundation.org',
                    recipient_list=[contact.useremail],
                    fail_silently=True
                )
            except Exception:
                pass
                
        # Send cohort invitation email if assigned cohort changed
        if cohort_changed and cohort_val:
            try:
                send_mail(
                    subject='Welcome to your Cohort! | She Can Foundation',
                    message=f"Dear {contact.username},\n\nCongratulations! You have been successfully assigned to our specialized training track: '{cohort_val}'.\n\nYour assigned mentor will reach out in the next 48 hours with syllabus materials and study rings details.\n\nLog in to your Student Portal to view resources.\n\nBest Regards,\nShe Can Foundation Team",
                    from_email='admissions@shecanfoundation.org',
                    recipient_list=[contact.useremail],
                    fail_silently=True
                )
            except Exception:
                pass
                
        return JsonResponse({
            'success': True,
            'is_verified': contact.is_verified,
            'status': contact.status,
            'assigned_cohort': contact.assigned_cohort or ''
        })
        
    return JsonResponse({'error': 'Invalid Request'}, status=400)


@login_required(login_url='student_login')
def admin_export_csv(request):
    if not request.user.is_superuser:
        return HttpResponse('Unauthorized', status=403)
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="SheCan_Applicants_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Gender', 'City', 'State', 'Verified', 'Status', 'Assigned Cohort', 'Submitted Date'])
    
    for c in Contact.objects.all():
        writer.writerow([
            c.id, c.username, c.useremail, c.userphone, 
            c.get_usergender_display(), c.usercity, c.userstate, 
            c.is_verified, c.status, c.assigned_cohort or 'None',
            c.created_at.strftime('%Y-%m-%d %H:%M')
        ])
        
    return response


# ── 4. ADMIN DASHBOARD WITH ANALYTICS ──
def dashboard(request):
    # Simple redirect to custom login if not authenticated or not staff
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/login/?next=/dashboard/')

    data = Contact.objects.all()
    verified_users = Contact.objects.filter(is_verified=True).count()
    
    # Calculate Stats for Charts
    # 1. Cohort Distribution based on parsing interests or defaults
    # Let's count how many choose Coding vs Design vs Data from database search
    coding_count = Contact.objects.filter(usermessage__icontains="Coding & Development").count()
    design_count = Contact.objects.filter(usermessage__icontains="UI/UX Design").count()
    data_count = Contact.objects.filter(usermessage__icontains="Data Science").count()
    other_count = max(0, data.count() - (coding_count + design_count + data_count))
    
    # 2. State-wise distribution
    state_stats = Contact.objects.values('userstate').annotate(total=Count('id')).order_by('-total')[:5]
    state_labels = [s['userstate'] for s in state_stats]
    state_values = [s['total'] for s in state_stats]
    
    # 3. Status wise distribution
    pending_count = Contact.objects.filter(status='Pending').count()
    approved_count = Contact.objects.filter(status='Approved').count()
    rejected_count = Contact.objects.filter(status='Rejected').count()

    context = {
        'data': data,
        'verified_users': verified_users,
        'stats': {
            'coding': coding_count,
            'design': design_count,
            'data_sci': data_count,
            'other': other_count,
            'pending': pending_count,
            'approved': approved_count,
            'rejected': rejected_count,
            'state_labels': state_labels,
            'state_values': state_values,
        }
    }

    return render(request, 'dashboard.html', context)