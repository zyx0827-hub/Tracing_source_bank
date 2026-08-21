from django.shortcuts import render


# Create your views here.
from rest_framework import viewsets

from apps.impeachform.models import ImpeachForm
from apps.impeachform.serializers import impeachformSerializer
class impeachformViewSet(viewsets.ModelViewSet):
    """用户表视图集"""
    queryset = ImpeachForm.objects.all()
    serializer_class = impeachformSerializer