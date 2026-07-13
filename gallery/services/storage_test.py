import os
from gallery.services.supabase_storage import supabase


def test_upload():

    local_file = "static/img/Google-logo.png"

    with open(local_file, "rb") as f:
        supabase.storage.from_("gallery-images").upload(
            "test/google-logo.png",
            f.read(),
            {"content-type": "image/png"}
        )

    print("Upload successful!")