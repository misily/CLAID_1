from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UploadFileSerializer
from rest_framework.permissions import IsAuthenticated
import os

class UploadFileView(APIView):
    permission_classes = [IsAuthenticated]  
    def post(self, request, format=None):
        serializer = UploadFileSerializer(data=request.data)
        if serializer.is_valid():
            files = serializer.save()
            return Response({'files': files}, status=201)
        return Response(serializer.errors, status=400)