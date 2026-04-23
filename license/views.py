# views.py
import jwt
from datetime import datetime, timedelta, timezone as dt_timezone

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import License


@api_view(["GET"])
def check_license(request):
    tenant = request.headers.get("X-Tenant-ID")
    if not tenant:
        return Response({"detail": "Missing tenant."}, status=400)

    try:
        license_obj = License.objects.get(tenant=tenant)
    except License.DoesNotExist:
        return Response({"detail": "License not found for tenant."}, status=403)

    if not license_obj.is_valid:
        return Response({"detail": "License expired or inactive."}, status=403)

    now = datetime.now(dt_timezone.utc)

    # ✅ End of the last valid day, not midnight start
    end_datetime = (
        datetime.combine(license_obj.end_date, datetime.min.time()) + timedelta(days=1)
    ).replace(tzinfo=dt_timezone.utc)

    jwt_expiry = min(now + timedelta(hours=settings.LICENSE_JWT_TTL_HOURS), end_datetime)

    payload = {
        "tenant": tenant,
        "is_valid": license_obj.is_valid,           # ✅ consumed by frontend if/else
        "is_active": license_obj.is_active,          # ✅ useful for manual kill-switch
        "end_date": license_obj.end_date.isoformat(),
        "days_remaining": license_obj.days_remaining, # ✅ consumed by frontend warning
        "iat": now,
        "exp": jwt_expiry,
    }

    token = jwt.encode(payload, settings.LICENSE_JWT_PRIVATE_KEY, algorithm="RS256")
    return Response({"token": token})