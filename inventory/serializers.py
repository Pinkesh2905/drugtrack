from rest_framework import serializers
from .models import DrugBatch


class DrugBatchSerializer(serializers.ModelSerializer):
    """
    Serializer for DrugBatch model with additional computed fields
    """
    expiry_status = serializers.CharField(read_only=True)
    days_to_expiry = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    qr_data = serializers.CharField(read_only=True)
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DrugBatch
        fields = [
            'id',
            'name',
            'manufacturer', 
            'batch_number',
            'manufacture_date',
            'expiry_date',
            'quantity',
            'qr_code',
            'qr_code_url',
            'qr_data',
            'expiry_status',
            'days_to_expiry',
            'is_expired',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'qr_code', 'created_at', 'updated_at']
    
    def get_qr_code_url(self, obj):
        """Get the full URL for the QR code image"""
        if obj.qr_code:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code.url)
            return obj.qr_code.url
        return None
    
    def validate_batch_number(self, value):
        """Validate batch number uniqueness"""
        if value:
            value = value.strip().upper()
            # Check if batch number already exists (exclude current instance for updates)
            instance = getattr(self, 'instance', None)
            queryset = DrugBatch.objects.filter(batch_number=value)
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    "A batch with this number already exists."
                )
        return value
    
    def validate(self, data):
        """Validate manufacture and expiry dates"""
        manufacture_date = data.get('manufacture_date')
        expiry_date = data.get('expiry_date')
        
        if manufacture_date and expiry_date:
            if manufacture_date >= expiry_date:
                raise serializers.ValidationError({
                    'expiry_date': 'Expiry date must be after manufacture date.'
                })
        
        return data


class DrugBatchListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for list views (lighter payload)
    """
    expiry_status = serializers.CharField(read_only=True)
    days_to_expiry = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = DrugBatch
        fields = [
            'id',
            'name',
            'manufacturer',
            'batch_number', 
            'expiry_date',
            'quantity',
            'expiry_status',
            'days_to_expiry',
            'is_expired',
            'created_at'
        ]


class DrugVerificationSerializer(serializers.Serializer):
    """
    Serializer for drug verification requests
    """
    batch_number = serializers.CharField(max_length=100)
    
    def validate_batch_number(self, value):
        """Clean and validate batch number"""
        if value:
            return value.strip().upper()
        return value


class QRVerificationSerializer(serializers.Serializer):
    """
    Serializer for QR code verification requests
    """
    qr_data = serializers.CharField()
    
    def validate_qr_data(self, value):
        """Basic validation for QR data format"""
        if not value or '|' not in value:
            raise serializers.ValidationError(
                "Invalid QR code format. Expected format: batch_number|drug_name|expiry_date"
            )
        return value


class InventoryStatsSerializer(serializers.Serializer):
    """
    Serializer for inventory statistics
    """
    total_batches = serializers.IntegerField()
    total_quantity = serializers.IntegerField()
    expired_batches = serializers.IntegerField()
    expiring_soon = serializers.IntegerField()
    manufacturers_count = serializers.IntegerField()
    low_stock_alerts = serializers.IntegerField(required=False)
    
    # Additional breakdown stats
    by_manufacturer = serializers.DictField(required=False)
    by_expiry_status = serializers.DictField(required=False)