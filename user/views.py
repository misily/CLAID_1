from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from my_settings import GOOGLE_API_KEY

class GoogleLogin(APIView):

    def get(self, request):
        return Response(GOOGLE_API_KEY, status=status.HTTP_200_OK)



