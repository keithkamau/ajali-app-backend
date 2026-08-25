from rest_framework import permissions, viewsets

from .models import Incident
from .serializers import IncidentSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Incident.objects.filter(user=self.request.user).prefetch_related("media", "status_history")

    def perform_create(self, serializer):
        incident = serializer.save(user=self.request.user)
        incident.status_history.create(new_status=incident.status, changed_by=self.request.user)