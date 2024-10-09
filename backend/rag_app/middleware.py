# backend/rag_app/middleware.py
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from .models import User
from backend.rag_app.config import ACCOUNT_TIERS

def check_usage_limits(get_response):
    def middleware(request):
        if request.user.is_authenticated:
            now = timezone.now()
            if now - request.user.last_query_reset > relativedelta(months=1):
                request.user.queries_this_month = 0
                request.user.last_query_reset = now
                request.user.save()

            if request.user.account_tier == 'free':
                if request.user.queries_this_month >= ACCOUNT_TIERS['free']['monthly_query_limit']:
                    return JsonResponse({'error': 'Monthly query limit reached'}, status=403)

            request.user.queries_this_month += 1
            request.user.save()

        response = get_response(request)
        return response
    return middleware