from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Q, Count
from collections import defaultdict

from .models import DrugBatch
from .serializers import (
    DrugBatchSerializer, 
    DrugBatchListSerializer,
    DrugVerificationSerializer,
    QRVerificationSerializer,
    InventoryStatsSerializer
)
from .qr_utils import verify_qr_data


class DrugBatchListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating drug batches
    GET: List all drug batches with filtering and search
    POST: Create new drug batch
    """
    queryset = DrugBatch.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'expiry_status']
    search_fields = ['name', 'manufacturer', 'batch_number']
    ordering_fields = ['created_at', 'expiry_date', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializer for list vs create"""
        if self.request.method == 'GET':
            return DrugBatchListSerializer
        return DrugBatchSerializer
    
    def get_queryset(self):
        """Custom filtering for expiry status"""
        queryset = super().get_queryset()
        expiry_filter = self.request.query_params.get('expiry_status', None)
        
        if expiry_filter:
            today = timezone.now().date()
            if expiry_filter == 'expired':
                queryset = queryset.filter(expiry_date__lt=today)
            elif expiry_filter == 'expiring':
                from datetime import timedelta
                expiring_date = today + timedelta(days=30)
                queryset = queryset.filter(
                    expiry_date__lte=expiring_date, 
                    expiry_date__gte=today
                )
            elif expiry_filter == 'warning':
                from datetime import timedelta
                warning_date = today + timedelta(days=90)
                queryset = queryset.filter(
                    expiry_date__lte=warning_date, 
                    expiry_date__gte=today
                )
            elif expiry_filter == 'good':
                from datetime import timedelta
                good_date = today + timedelta(days=90)
                queryset = queryset.filter(expiry_date__gt=good_date)
        
        return queryset


class DrugBatchDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting drug batches
    GET: Retrieve specific batch details
    PUT/PATCH: Update batch information
    DELETE: Delete batch
    """
    queryset = DrugBatch.objects.all()
    serializer_class = DrugBatchSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Public endpoint for verification
def verify_drug_api(request):
    """
    API endpoint for drug verification
    GET: Verify by batch number (query parameter)
    POST: Verify by batch number (request body)
    """
    if request.method == 'GET':
        batch_number = request.query_params.get('batch_number', '').strip().upper()
        
        if not batch_number:
            return Response({
                'success': False,
                'message': 'batch_number parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    else:  # POST
        serializer = DrugVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        batch_number = serializer.validated_data['batch_number']
    
    try:
        batch = DrugBatch.objects.get(batch_number__iexact=batch_number)
        serializer = DrugBatchSerializer(batch, context={'request': request})
        
        return Response({
            'success': True,
            'valid': True,
            'message': 'Drug batch verified successfully',
            'batch': serializer.data
        })
        
    except DrugBatch.DoesNotExist:
        return Response({
            'success': True,
            'valid': False,
            'message': 'Invalid batch number. This drug batch does not exist in our system.',
            'batch_number': batch_number
        })


@api_view(['POST'])
@permission_classes([AllowAny])  # Public endpoint for QR verification
def verify_qr_api(request):
    """
    API endpoint for QR code verification
    POST: Verify drug by QR code data
    """
    serializer = QRVerificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    qr_data = serializer.validated_data['qr_data']
    
    # Parse QR data
    parsed_data = verify_qr_data(qr_data)
    
    if not parsed_data['is_valid']:
        return Response({
            'success': True,
            'valid': False,
            'message': parsed_data.get('error', 'Invalid QR code format')
        })
    
    # Try to find the batch
    try:
        batch = DrugBatch.objects.get(
            batch_number__iexact=parsed_data['batch_number']
        )
        
        serializer = DrugBatchSerializer(batch, context={'request': request})
        
        return Response({
            'success': True,
            'valid': True,
            'message': 'QR code verified successfully',
            'parsed_qr_data': parsed_data,
            'batch': serializer.data
        })
        
    except DrugBatch.DoesNotExist:
        return Response({
            'success': True,
            'valid': False,
            'message': 'QR code format is valid but batch not found in system',
            'parsed_qr_data': parsed_data
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_stats_api(request):
    """
    API endpoint for inventory statistics
    """
    today = timezone.now().date()
    from datetime import timedelta
    
    # Basic stats
    total_batches = DrugBatch.objects.count()
    total_quantity = sum([batch.quantity for batch in DrugBatch.objects.all()])
    expired_batches = DrugBatch.objects.filter(expiry_date__lt=today).count()
    expiring_soon = DrugBatch.objects.filter(
        expiry_date__lte=today + timedelta(days=30),
        expiry_date__gte=today
    ).count()
    manufacturers_count = DrugBatch.objects.values('manufacturer').distinct().count()
    
    # Additional stats
    by_manufacturer = {}
    manufacturer_stats = DrugBatch.objects.values('manufacturer').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for stat in manufacturer_stats:
        by_manufacturer[stat['manufacturer']] = stat['count']
    
    # Expiry status breakdown
    warning_count = DrugBatch.objects.filter(
        expiry_date__lte=today + timedelta(days=90),
        expiry_date__gt=today + timedelta(days=30)
    ).count()
    
    good_count = DrugBatch.objects.filter(
        expiry_date__gt=today + timedelta(days=90)
    ).count()
    
    by_expiry_status = {
        'good': good_count,
        'warning': warning_count,
        'expiring_soon': expiring_soon,
        'expired': expired_batches
    }
    
    stats_data = {
        'total_batches': total_batches,
        'total_quantity': total_quantity,
        'expired_batches': expired_batches,
        'expiring_soon': expiring_soon,
        'manufacturers_count': manufacturers_count,
        'by_manufacturer': by_manufacturer,
        'by_expiry_status': by_expiry_status
    }
    
    serializer = InventoryStatsSerializer(stats_data)
    return Response({
        'success': True,
        'stats': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def low_stock_alerts_api(request):
    """
    API endpoint for low stock alerts
    """
    threshold = int(request.query_params.get('threshold', 10))
    
    low_stock_batches = DrugBatch.objects.filter(
        quantity__lte=threshold
    ).order_by('quantity')
    
    serializer = DrugBatchListSerializer(
        low_stock_batches, 
        many=True, 
        context={'request': request}
    )
    
    return Response({
        'success': True,
        'threshold': threshold,
        'count': low_stock_batches.count(),
        'batches': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expiry_alerts_api(request):
    """
    API endpoint for expiry alerts
    """
    days = int(request.query_params.get('days', 30))
    today = timezone.now().date()
    alert_date = today + timezone.timedelta(days=days)
    
    expiring_batches = DrugBatch.objects.filter(
        expiry_date__lte=alert_date,
        expiry_date__gte=today
    ).order_by('expiry_date')
    
    serializer = DrugBatchListSerializer(
        expiring_batches, 
        many=True, 
        context={'request': request}
    )
    
    return Response({
        'success': True,
        'days_threshold': days,
        'count': expiring_batches.count(),
        'batches': serializer.data
    })