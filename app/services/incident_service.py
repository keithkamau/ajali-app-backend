from django.db import transaction

from app.models import Incident, IncidentMedia, IncidentStatusHistory
from app.validators import validate_media_upload


@transaction.atomic
def create_incident(*, user, validated_data):
	incident = Incident.objects.create(user=user, **validated_data)
	IncidentStatusHistory.objects.create(
		incident=incident,
		new_status=incident.status,
		changed_by=user,
	)
	return incident


@transaction.atomic
def change_status(*, incident, changed_by, new_status, comment=""):
	if new_status == incident.status:
		raise ValueError("The new status must differ from the current status.")

	old_status = incident.status
	incident.status = new_status
	incident.save(update_fields=("status", "updated_at"))
	IncidentStatusHistory.objects.create(
		incident=incident,
		old_status=old_status,
		new_status=new_status,
		changed_by=changed_by,
		comment=comment,
	)
	return incident


def attach_media(*, incident, media_type, media_url, mime_type, file_size_bytes, public_id=""):
	validate_media_upload(
		media_type=media_type,
		mime_type=mime_type,
		file_size_bytes=file_size_bytes,
	)
	return IncidentMedia.objects.create(
		incident=incident,
		media_type=media_type,
		media_url=media_url,
		mime_type=mime_type,
		file_size_bytes=file_size_bytes,
		public_id=public_id,
	)
