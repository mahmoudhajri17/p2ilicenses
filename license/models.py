# models.py
import uuid
from django.db import models
from django.utils import timezone
import secrets

class License(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=255) 
    company_id = models.CharField(max_length=100, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    allowed_domains = models.JSONField(default=list, blank=True)  # ← add this
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_valid(self):
        return self.is_active and self.end_date >= timezone.now().date()

    @property
    def days_remaining(self):
        return max((self.end_date - timezone.now().date()).days, 0)

    def __str__(self):
        return f"{self.company_name} ({'valid' if self.is_valid else 'invalid'})"