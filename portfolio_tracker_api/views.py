from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def welcome_view(request):
    return Response({"message": "Welcome to my DRF API!"})


@require_http_methods(["GET", "HEAD"])
def health(request):
    return JsonResponse({"status": "ok"})
