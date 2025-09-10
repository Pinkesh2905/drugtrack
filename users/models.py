from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """
    Custom User model extending AbstractUser with role-based access
    """
    ROLE_CHOICES = [
        ('pharma', 'Pharmaceutical Company'),
        ('hospital', 'Hospital'),
        ('regulator', 'Regulator'),
        ('patient', 'Patient'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='patient',
        help_text="Select user role for appropriate dashboard access"
    )
    
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Contact phone number"
    )
    
    organization = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Organization/Hospital/Company name"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def get_dashboard_url(self):
        """Return appropriate dashboard URL based on user role"""
        dashboard_urls = {
            'pharma': reverse("dashboard:pharma_dashboard"),
            'hospital': reverse("dashboard:hospital_dashboard"),
            'regulator': reverse("dashboard:regulator_dashboard"),
            'patient': reverse("dashboard:patient_dashboard"),
        }
        return dashboard_urls.get(self.role, reverse("dashboard:home"))
    
    def get_role_display_name(self):
        """Return the human-readable role name"""
        return dict(self.ROLE_CHOICES).get(self.role, "Unknown")
    
    class Meta:
        db_table = 'users_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
