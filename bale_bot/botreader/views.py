import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .services.services import get_new_messages_and_save

logger = logging.getLogger(__name__)

class ReaderAPI(APIView):
    def get(self, request):
        try:
            get_new_messages_and_save()
        except ValueError as e:
            logger.error(e)
            return Response(status=500, message="Can't receive data bot data")
        return Response(status=status.HTTP_200_OK)
