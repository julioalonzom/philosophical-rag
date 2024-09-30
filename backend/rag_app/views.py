import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import QuerySerializer
from rag_core.rag_engine import RAGEngine
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
        response["Access-Control-Allow-Headers"] = "Content-Type"
        
        return response

    def options(self, request):
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response