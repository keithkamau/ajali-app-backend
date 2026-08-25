from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from app.models import Incident, IncidentStatusHistory
from app.services.incident_service import change_status, create_incident


class IncidentApiTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username="reporter", password="test-password")
		self.other_user = get_user_model().objects.create_user(username="other", password="test-password")
		self.client = APIClient()
		self.client.force_authenticate(self.user)
		self.payload = {
			"title": "Blocked drainage",
			"description": "Water is covering the entrance.",
			"type": "flood",
			"location_lat": -1.286389,
			"location_lng": 36.817223,
			"location_address": "City Market, Nairobi",
			"is_anonymous": False,
		}

	def test_authenticated_user_can_create_incident_and_initial_history(self):
		response = self.client.post("/api/incidents/", self.payload, format="json")

		self.assertEqual(response.status_code, 201)
		incident = Incident.objects.get(pk=response.data["id"])
		self.assertEqual(incident.user, self.user)
		self.assertEqual(incident.status, Incident.Status.REPORTED)
		self.assertTrue(IncidentStatusHistory.objects.filter(incident=incident, old_status__isnull=True).exists())

	def test_user_cannot_see_another_users_incident(self):
		Incident.objects.create(user=self.other_user, **self.payload)

		response = self.client.get("/api/incidents/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 0)

	def test_status_change_creates_history(self):
		incident = create_incident(user=self.user, validated_data=self.payload)

		change_status(
			incident=incident,
			changed_by=self.user,
			new_status=Incident.Status.IN_PROGRESS,
			comment="Response team assigned.",
		)

		incident.refresh_from_db()
		history = incident.status_history.first()
		self.assertEqual(incident.status, Incident.Status.IN_PROGRESS)
		self.assertEqual(history.old_status, Incident.Status.REPORTED)
		self.assertEqual(history.comment, "Response team assigned.")
