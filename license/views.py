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
    # ✅ ONLY SOURCE OF TRUTH
    tenant = request.headers.get("X-Tenant-ID")
    if not tenant:
        return Response({"detail": "Missing tenant."}, status=400)

    try:
        license = License.objects.get(domain=tenant)
    except License.DoesNotExist:
        return Response({"detail": "License not found for tenant."}, status=403)

    # ✅ validate license
    if not license.is_valid:
        return Response({"detail": "License expired or inactive."}, status=403)

    # ⏱ JWT expiry logic
    now = datetime.now(dt_timezone.utc)

    end_datetime = datetime.combine(
        license.end_date,
        datetime.min.time()
    ).replace(tzinfo=dt_timezone.utc)

    jwt_expiry = min(
        now + timedelta(hours=settings.LICENSE_JWT_TTL_HOURS),
        end_datetime
    )

    # 🔐 token payload
    payload = {
        "tenant": tenant,
        "is_active": license.is_active,
        "is_valid": license.is_valid,
        "end_date": license.end_date.isoformat(),
        "days_remaining": license.days_remaining,
        "iat": now,
        "exp": jwt_expiry,
    }

    token = jwt.encode(
        payload,
        settings.LICENSE_JWT_PRIVATE_KEY,
        algorithm="RS256"
    )

    return Response({"token": token})