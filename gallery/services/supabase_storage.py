import mimetypes
import uuid
from supabase import create_client
from django.conf import settings


supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY
)


def upload_gallery_image(image_bytes, filename):

    content_type = (
        mimetypes.guess_type(filename)[0]
        or "application/octet-stream"
    )

    supabase.storage \
        .from_("gallery-images") \
        .upload(
            path=filename,
            file=image_bytes,
            file_options={
                "content-type": content_type,
                "upsert": "true"
            }
        )

    return filename


def get_public_url(filename):

    return (
        supabase.storage
        .from_("gallery-images")
        .get_public_url(filename)
    )


def delete_gallery_image(filename):

    supabase.storage \
        .from_("gallery-images") \
        .remove([filename])
    
def upload_generated_image(image_bytes, filename):

    content_type = (
        mimetypes.guess_type(filename)[0]
        or "application/octet-stream"
    )

    supabase.storage \
        .from_("generated-images") \
        .upload(
            path=filename,
            file=image_bytes,
            file_options={
                "content-type": content_type,
                "upsert": "true"
            }
        )

    return filename


def get_generated_public_url(filename):

    return (
        supabase.storage
        .from_("generated-images")
        .get_public_url(filename)
    )


def delete_generated_image(filename):

    supabase.storage \
        .from_("generated-images") \
        .remove([filename])
    

def upload_profile_picture(image_bytes, filename):

    content_type = (
        mimetypes.guess_type(filename)[0]
        or "application/octet-stream"
    )

    supabase.storage \
        .from_("profile-pictures") \
        .upload(
            path=filename,
            file=image_bytes,
            file_options={
                "content-type": content_type,
                "upsert": "true"
            }
        )

    return filename


def get_profile_picture_url(filename):

    return (
        supabase.storage
        .from_("profile-pictures")
        .get_public_url(filename)
    )


def delete_profile_picture(filename):

    supabase.storage \
        .from_("profile-pictures") \
        .remove([filename])
    

def upload_audio(audio_bytes, filename):

    content_type = (
        mimetypes.guess_type(filename)[0]
        or "application/octet-stream"
    )

    supabase.storage \
        .from_("audio-notes") \
        .upload(
            path=filename,
            file=audio_bytes,
            file_options={
                "content-type": content_type,
                "upsert": "true"
            }
        )

    return filename


def get_audio_public_url(filename):

    return (
        supabase.storage
        .from_("audio-notes")
        .get_public_url(filename)
    )


def delete_audio(filename):

    supabase.storage \
        .from_("audio-notes") \
        .remove([filename])