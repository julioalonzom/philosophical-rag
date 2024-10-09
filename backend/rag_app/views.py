import logging
import stripe
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import QuerySerializer
from rag_core.rag_engine import RAGEngine
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import User
from .config import ACCOUNT_TIERS
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

# Initialize RAGEngine once
rag_engine = RAGEngine()

@method_decorator(csrf_exempt, name='dispatch')
class QueryView(APIView):
    def post(self, request):
        logger.info(f"Received query: {request.data}")
        serializer = QuerySerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            user = request.user

            # Check if user is authenticated
            if user.is_authenticated:
                # Check usage limits for authenticated users
                if user.account_tier == 'free' and user.queries_this_month >= ACCOUNT_TIERS['free']['monthly_query_limit']:
                    return JsonResponse({'error': 'Monthly query limit reached'}, status=status.HTTP_403_FORBIDDEN)
                
                # Update user's query count
                user.queries_this_month += 1
                user.save()
            else:
                # For anonymous users, we don't track usage
                pass

            try:
                response_text, citations = rag_engine.process_query(query)
                logger.info(f"Processed query. Response length: {len(response_text)}, Citations: {len(citations)}")
                
                response = JsonResponse({
                    'response': response_text,
                    'citations': citations
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                response = JsonResponse({
                    'error': 'An error occurred while processing your query.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warning(f"Invalid query data: {serializer.errors}")
            response = JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': settings.STRIPE_PRICE_ID,
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=request.build_absolute_uri('/success'),
                cancel_url=request.build_absolute_uri('/cancel'),
                client_reference_id=request.user.id,
            )
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['client_reference_id']
        user = User.objects.get(id=user_id)
        user.account_tier = 'premium'
        user.save()

    return HttpResponse(status=200)

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page after login
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    return JsonResponse({'error': 'GET request received. Use POST to login.'}, status=405)