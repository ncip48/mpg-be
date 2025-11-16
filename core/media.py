import os

from django.conf import settings


def media_to_path(val):
    if not val:
        return None

    # If MEDIA_URL = "/media/"
    if val.startswith(settings.MEDIA_URL):
        return os.path.join(settings.MEDIA_ROOT, val.replace(settings.MEDIA_URL, ""))

    return val
