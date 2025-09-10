from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import DrugBatch


@admin.register(DrugBatch)
class DrugBatchAdmin(admin.ModelAdmin):
    list_display = [
        'batch_number',
        'name', 
        'manufacturer', 
        'quantity',
        'manufacture_date',
        'expiry_date',
        'expiry_status_badge',
        'qr_code_preview',
        'created_at'
    ]
    
    list_filter = [
        'manufacturer',
        'manufacture_date',
        'expiry_date',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'manufacturer', 
        'batch_number'
    ]
    
    readonly_fields = [
        'id',
        'qr_code_preview',
        'qr_data',
        'days_to_expiry',
        'expiry_status',
        'is_expired',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'manufacturer', 'batch_number')
        }),
        ('Dates & Quantity', {
            'fields': ('manufacture_date', 'expiry_date', 'quantity')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_code_preview', 'qr_data'),
            'classes': ('collapse',)
        }),
        ('Status Information', {
            'fields': ('expiry_status', 'days_to_expiry', 'is_expired'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'expiry_date'
    
    def expiry_status_badge(self, obj):
        """Display expiry status with color-coded badge"""
        status = obj.expiry_status
        colors = {
            'Good': '#28a745',
            'Warning': '#ffc107',
            'Expiring Soon': '#fd7e14', 
            'Expired': '#dc3545'
        }
        color = colors.get(status, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 12px; font-weight: bold;">{}</span>',
            color, status
        )
    expiry_status_badge.short_description = 'Status'
    expiry_status_badge.admin_order_field = 'expiry_date'
    
    def qr_code_preview(self, obj):
        """Display QR code preview in admin"""
        if obj.qr_code:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.qr_code.url
            )
        return "No QR Code"
    qr_code_preview.short_description = 'QR Preview'
    
    def get_queryset(self, request):
        """Optimize queryset for admin list view"""
        return super().get_queryset(request).select_related()
    
    actions = ['mark_as_expired', 'regenerate_qr_codes']
    
    def mark_as_expired(self, request, queryset):
        """Custom admin action to mark batches as expired"""
        today = timezone.now().date()
        updated = queryset.filter(expiry_date__gte=today).update(expiry_date=today)
        
        if updated:
            self.message_user(request, f'{updated} batch(es) marked as expired.')
        else:
            self.message_user(request, 'No batches were updated.')
    mark_as_expired.short_description = "Mark selected batches as expired"
    
    def regenerate_qr_codes(self, request, queryset):
        """Regenerate QR codes for selected batches"""
        updated_count = 0
        
        for batch in queryset:
            # Clear existing QR code
            if batch.qr_code:
                batch.qr_code.delete()
                batch.qr_code = None
            
            # Save will trigger QR code regeneration
            batch.save()
            updated_count += 1
        
        self.message_user(
            request, 
            f'QR codes regenerated for {updated_count} batch(es).'
        )
    regenerate_qr_codes.short_description = "Regenerate QR codes for selected batches"
    
    def save_model(self, request, obj, form, change):
        """Override save to handle QR code generation"""
        super().save_model(request, obj, form, change)
        
        # Add success message
        if not change:  # New object
            self.message_user(
                request,
                f'Drug batch "{obj.name}" created with QR code generated successfully.'
            )