# views.py
import jwt
from datetime import datetime, timedelta, timezone as dt_timezone
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import License

# views.py
@api_view(["GET"])
def check_license(request, company_id):
    try:
        license = License.objects.get(company_id=company_id)
    except License.DoesNotExist:
        return Response({"detail": "Not found."}, status=404)

    # Domain check — only runs if allowed_domains is populated
    origin = request.headers.get("Origin", "")

    if not license.allowed_domains or not any(domain in origin for domain in license.allowed_domains):
        return Response({"detail": "Domain not allowed."}, status=403)

    # views.py — add after domain check
    if not license.is_valid:
        return Response({"detail": "License expired or inactive."}, status=403)

    now = datetime.now(dt_timezone.utc)
    end_datetime = datetime.combine(
        license.end_date, datetime.min.time()
    ).replace(tzinfo=dt_timezone.utc)
    jwt_expiry = min(now + timedelta(hours=settings.LICENSE_JWT_TTL_HOURS), end_datetime)

    payload = {
        "company_id": str(company_id),
        "is_active": license.is_active,
        "is_valid": license.is_valid,
        "end_date": license.end_date.isoformat(),
        "days_remaining": license.days_remaining,
        "iat": now,
        "exp": jwt_expiry,
    }

    token = jwt.encode(payload, settings.LICENSE_JWT_PRIVATE_KEY, algorithm="RS256")
    return Response({"token": token})  