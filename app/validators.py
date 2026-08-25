from rest_framework import serializers


MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_VIDEO_BYTES = 50 * 1024 * 1024
ALLOWED_MEDIA_TYPES = {
    "image": ("image/jpeg", "image/png", "image/webp"),
    "video": ("video/mp4", "video/quicktime", "video/webm"),
}


def validate_media_upload(*, media_type, mime_type, file_size_bytes):
    allowed_mime_types = ALLOWED_MEDIA_TYPES.get(media_type)
    if allowed_mime_types is None:
        raise serializers.ValidationError("Media type must be image or video.")
    if mime_type not in allowed_mime_types:
        raise serializers.ValidationError(f"Unsupported MIME type for {media_type}.")

    max_size = MAX_IMAGE_BYTES if media_type == "image" else MAX_VIDEO_BYTES
    if file_size_bytes <= 0 or file_size_bytes > max_size:
        raise serializers.ValidationError(f"{media_type.title()} files must be smaller than {max_size // (1024 * 1024)} MB.")