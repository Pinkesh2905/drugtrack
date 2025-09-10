from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import timedelta
from inventory.models import DrugBatch


@login_required
def home(request):
    """General dashboard homepage (default for admins or fallback)."""
    today = now().date()
    soon = today + timedelta(days=30)

    total_batches = DrugBatch.objects.count()
    expired_count = DrugBatch.objects.filter(expiry_date__lt=today).count()
    expiring_soon_count = DrugBatch.objects.filter(expiry_date__range=[today, soon]).count()

    context = {
        "page_title": "Dashboard",
        "total_batches": total_batches,
        "expired_count": expired_count,
        "expiring_soon_count": expiring_soon_count,
    }
    return render(request, "dashboard/home.html", context)


@login_required
def patient_dashboard(request):
    return render(request, "dashboard/patient_dashboard.html", {"page_title": "Patient Dashboard"})


@login_required
def hospital_dashboard(request):
    today = now().date()
    soon = today + timedelta(days=30)
    expiring_soon = DrugBatch.objects.filter(expiry_date__range=[today, soon])
    context = {
        "page_title": "Hospital Dashboard",
        "expiring_soon": expiring_soon,
    }
    return render(request, "dashboard/hospital_dashboard.html", context)


@login_required
def pharma_dashboard(request):
    today = now().date()
    batches = DrugBatch.objects.all().order_by("-created_at")[:5]
    context = {
        "page_title": "Pharma Dashboard",
        "latest_batches": batches,
    }
    return render(request, "dashboard/pharma_dashboard.html", context)


@login_required
def regulator_dashboard(request):
    today = now().date()
    expired = DrugBatch.objects.filter(expiry_date__lt=today)
    context = {
        "page_title": "Regulator Dashboard",
        "expired_batches": expired,
    }
    return render(request, "dashboard/regulator_dashboard.html", context)
