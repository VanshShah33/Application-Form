from django.db import models
from django.contrib.auth.models import User

class Contact(models.Model):
    
    gender_choice=[
        ('M','Male'),
        ('F','Female'),
        ('O','Other'),
    ]

    state_choice = [
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
        ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
        ('Chandigarh', 'Chandigarh'),
        ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
        ('Delhi', 'Delhi'),
        ('Jammu and Kashmir', 'Jammu and Kashmir'),
        ('Ladakh', 'Ladakh'),
        ('Lakshadweep', 'Lakshadweep'),
        ('Puducherry', 'Puducherry'),
]
    
    username = models.CharField(max_length=100)
    useremail = models.EmailField(max_length=100)
    userphone = models.CharField(max_length=15)
    userdob = models.DateField(verbose_name="Date of Birth")
    usergender = models.CharField(max_length=1,choices=gender_choice)
    usercity = models.CharField(max_length=100)
    userstate = models.CharField(max_length=100 , choices=state_choice)
    usermessage = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending', choices=[('Pending','Pending'), ('Approved','Approved'), ('Rejected','Rejected')])
    assigned_cohort = models.CharField(max_length=100, null=True, blank=True, choices=[('Coding & Development','Coding & Development'), ('UI/UX Design','UI/UX Design'), ('Data Science & AI','Data Science & AI')])
    
    def __str__(self):
        return self.username
    
    
    
