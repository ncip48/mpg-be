import secrets


def default_subid_generator(nbytes: int = 48):
    return secrets.token_urlsafe(nbytes)