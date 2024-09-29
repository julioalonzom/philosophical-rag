import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import QuerySerializer
from rag_core.rag_engine import RAGEngine

logger = logging.getLogger(__name__)

# Initialize RAGEngine once
rag_engine = RAGEngine()

class QueryView(APIView):
    def post(self, request):
        logger.info(f"Received query: {request.data}")
        serializer = QuerySerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            try:
                response, citations = rag_engine.process_query(query)
                logger.info(f"Processed query. Response length: {len(response)}, Citations: {len(citations)}")
                return Response({
                    'response': response,
                    'citations': citations
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                return Response({
                    'error': 'An error occurred while processing your query.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.warning(f"Invalid query data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)