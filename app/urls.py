from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IncidentViewSet


router = DefaultRouter()
router.register("incidents", IncidentViewSet, basename="incident")

urlpatterns = [path("", include(router.urls))]