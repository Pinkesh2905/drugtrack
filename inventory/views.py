from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
import json
import csv

from .models import DrugBatch
from .forms import DrugBatchForm, DrugVerificationForm, DrugSearchForm
from .qr_utils import verify_qr_data


@login_required
def add_batch(request):
    """
    Add a new drug batch with automatic QR code generation
    """
    if request.method == 'POST':
        form = DrugBatchForm(request.POST)
        if form.is_valid():
            try:
                batch = form.save()
                messages.success(
                    request, 
                    f'Drug batch "{batch.name}" added successfully with QR code generated!'
                )
                return redirect('inventory:list_batches')
            except Exception as e:
                messages.error(request, f'Error saving batch: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DrugBatchForm()

    context = {
        'form': form,
        'title': 'Add New Drug Batch',
        'page_title': 'Add Drug Batch'
    }
    return render(request, 'inventory/add_batch.html', context)


@login_required
def list_batches(request):
    """
    List all drug batches with search and filtering capabilities
    """
    search_form = DrugSearchForm(request.GET)
    batches = DrugBatch.objects.all()
    
    # Apply search filters
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        expiry_status = search_form.cleaned_data.get('expiry_status')
        manufacturer = search_form.cleaned_data.get('manufacturer')
        
        if search_query:
            batches = batches.filter(
                Q(name__icontains=search_query) |
                Q(manufacturer__icontains=search_query) |
                Q(batch_number__icontains=search_query)
            )
        
        if manufacturer:
            batches = batches.filter(manufacturer__icontains=manufacturer)
        
        if expiry_status:
            today = timezone.now().date()
            if expiry_status == 'expired':
                batches = batches.filter(expiry_date__lt=today)
            elif expiry_status == 'expiring':
                from datetime import timedelta
                expiring_date = today + timedelta(days=30)
                batches = batches.filter(expiry_date__lte=expiring_date, expiry_date__gte=today)
            elif expiry_status == 'warning':
                from datetime import timedelta
                warning_date = today + timedelta(days=90)
                batches = batches.filter(expiry_date__lte=warning_date, expiry_date__gte=today)
            elif expiry_status == 'good':
                from datetime import timedelta
                good_date = today + timedelta(days=90)
                batches = batches.filter(expiry_date__gt=good_date)

    # Pagination
    paginator = Paginator(batches, 10)  # Show 10 batches per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_batches = DrugBatch.objects.count()
    expired_count = DrugBatch.objects.filter(expiry_date__lt=timezone.now().date()).count()
    expiring_soon_count = DrugBatch.objects.filter(
        expiry_date__lte=timezone.now().date() + timezone.timedelta(days=30),
        expiry_date__gte=timezone.now().date()
    ).count()

    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'title': 'Drug Inventory',
        'page_title': 'Drug Inventory',
        'total_batches': total_batches,
        'expired_count': expired_count,
        'expiring_soon_count': expiring_soon_count,
    }
    return render(request, 'inventory/list_batches.html', context)


def verify_drug(request, batch_number=None):
    """
    Verify drug authenticity by batch number from a form (POST) or URL (GET).
    """
    verification_form = DrugVerificationForm()
    batch = None
    verification_result = None
    
    # Handle POST request from the verification form
    if request.method == 'POST':
        verification_form = DrugVerificationForm(request.POST)
        if verification_form.is_valid():
            posted_batch_number = verification_form.cleaned_data['batch_number']
            # *** FIX: Redirect to the URL that accepts a batch_number ***
            # The URL name 'verify_drug_detail' matches '/verify/<str:batch_number>/'
            return redirect('inventory:verify_drug_detail', batch_number=posted_batch_number)

    # Handle GET request with batch number in the URL
    if batch_number:
        try:
            batch = DrugBatch.objects.get(batch_number__iexact=batch_number)
            verification_result = {
                'is_valid': True,
                'batch': batch,
                'message': 'Drug batch verified successfully!'
            }
        except DrugBatch.DoesNotExist:
            verification_result = {
                'is_valid': False,
                'message': 'Invalid batch number. This drug batch does not exist in our system.',
                'batch_number': batch_number
            }

    context = {
        'verification_form': verification_form,
        'batch': batch,
        'verification_result': verification_result,
        'batch_number': batch_number,
        'title': 'Drug Verification',
        'page_title': 'Verify Drug Authenticity'
    }
    return render(request, 'inventory/verify.html', context)


@login_required
def batch_detail(request, batch_id):
    """
    Display detailed information about a specific batch
    """
    batch = get_object_or_404(DrugBatch, id=batch_id)
    
    context = {
        'batch': batch,
        'title': f'Batch Details - {batch.name}',
        'page_title': f'Batch: {batch.batch_number}'
    }
    return render(request, 'inventory/batch_detail.html', context)


@login_required
@require_http_methods(["DELETE"])
def delete_batch(request, batch_id):
    """
    Delete a drug batch (AJAX endpoint)
    """
    try:
        batch = get_object_or_404(DrugBatch, id=batch_id)
        batch_name = batch.name
        batch.delete()
        return JsonResponse({
            'success': True,
            'message': f'Batch "{batch_name}" deleted successfully.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting batch: {str(e)}'
        })


@login_required
def export_expired_csv(request):
    """
    Generates and serves a CSV file of all expired drug batches.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expired_batches.csv"'

    writer = csv.writer(response)
    # Write the header row
    writer.writerow(['Batch Number', 'Drug Name', 'Manufacturer', 'Expiry Date', 'Quantity'])

    # Get expired batches
    expired_batches = DrugBatch.objects.filter(expiry_date__lt=timezone.now().date())
    
    # Write data rows
    for batch in expired_batches:
        writer.writerow([batch.batch_number, batch.name, batch.manufacturer, batch.expiry_date, batch.quantity])

    return response


@login_required
@require_POST # Ensures this view only accepts POST requests
def alert_all_expired(request):
    """
    Placeholder logic to handle the 'Alert All' action for expired batches.
    """
    expired_batches = DrugBatch.objects.filter(expiry_date__lt=timezone.now().date())
    
    # In a real app, you would loop through expired_batches and send alerts:
    # for batch in expired_batches:
    #     send_alert_for_batch(batch)

    count = expired_batches.count()
    if count > 0:
        messages.success(request, f'An alert has been successfully issued for {count} expired batch(es).')
    else:
        messages.info(request, 'No expired batches found to alert.')

    return redirect('dashboard:regulator_dashboard')


@login_required
def analytics_view(request):
    """
    Displays the analytics dashboard.
    (This is a placeholder and can be expanded later with real data)
    """
    context = {
        'title': 'Analytics Dashboard'
    }
    return render(request, 'inventory/analytics.html', context)


# API endpoint for QR code verification
@csrf_exempt
def api_verify_qr(request):
    """
    API endpoint to verify QR code data
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_data = data.get('qr_data', '')
            
            parsed_data = verify_qr_data(qr_data)
            
            if parsed_data['is_valid']:
                try:
                    batch = DrugBatch.objects.get(
                        batch_number__iexact=parsed_data['batch_number']
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'valid': True,
                        'batch': {
                            'id': str(batch.id),
                            'name': batch.name,
                            'manufacturer': batch.manufacturer,
                            'batch_number': batch.batch_number,
                            'manufacture_date': batch.manufacture_date.isoformat(),
                            'expiry_date': batch.expiry_date.isoformat(),
                            'quantity': batch.quantity,
                            'expiry_status': batch.expiry_status,
                            'days_to_expiry': batch.days_to_expiry,
                            'is_expired': batch.is_expired,
                        }
                    })
                    
                except DrugBatch.DoesNotExist:
                    return JsonResponse({
                        'success': True,
                        'valid': False,
                        'message': 'QR code format is valid but batch not found in system.'
                    })
            else:
                return JsonResponse({
                    'success': True,
                    'valid': False,
                    'message': parsed_data.get('error', 'Invalid QR code format.')
                })
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Server error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Only POST method allowed.'})


# Statistics endpoint for dashboard integration
@login_required
def inventory_stats(request):
    """
    Get inventory statistics for dashboard
    """
    today = timezone.now().date()
    
    stats = {
        'total_batches': DrugBatch.objects.count(),
        'total_quantity': sum([batch.quantity for batch in DrugBatch.objects.all()]),
        'expired_batches': DrugBatch.objects.filter(expiry_date__lt=today).count(),
        'expiring_soon': DrugBatch.objects.filter(
            expiry_date__lte=today + timezone.timedelta(days=30),
            expiry_date__gte=today
        ).count(),
        'manufacturers_count': DrugBatch.objects.values('manufacturer').distinct().count(),
    }
    
    return JsonResponse(stats)
