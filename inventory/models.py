import uuid
from django.db import models
from django.urls import reverse
from django.utils import timezone
import os
from .qr_utils import generate_qr_code


class DrugBatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Drug name")
    manufacturer = models.CharField(max_length=200, help_text="Manufacturer name")
    batch_number = models.CharField(max_length=100, unique=True, help_text="Unique batch number")
    manufacture_date = models.DateField(help_text="Date of manufacture")
    expiry_date = models.DateField(help_text="Expiry date")
    quantity = models.PositiveIntegerField(help_text="Quantity in stock")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, help_text="Auto-generated QR code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Drug Batch"
        verbose_name_plural = "Drug Batches"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.batch_number}"

    def save(self, *args, **kwargs):
        # Generate QR code if not exists
        if not self.qr_code:
            qr_data = f"{self.batch_number}|{self.name}|{self.expiry_date}"
            qr_filename = generate_qr_code(qr_data, self.batch_number)
            if qr_filename:
                self.qr_code = qr_filename
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # *** FIX: Point to the URL name that accepts a batch_number ***
        return reverse('inventory:verify_drug_detail', kwargs={'batch_number': self.batch_number})

    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    @property
    def days_to_expiry(self):
        delta = self.expiry_date - timezone.now().date()
        return delta.days if delta.days > 0 else 0

    @property
    def expiry_status(self):
        days = self.days_to_expiry
        if days <= 0:
            return "Expired"
        elif days <= 30:
            return "Expiring Soon"
        elif days <= 90:
            return "Warning"
        else:
            return "Good"

    @property
    def qr_data(self):
        return f"{self.batch_number}|{self.name}|{self.expiry_date}"
