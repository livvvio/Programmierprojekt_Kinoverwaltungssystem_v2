import hashlib


def hash_password(password: str) -> str:
    """Gibt den SHA-256-Hash des Passworts zurück."""
    return hashlib.sha256(password.encode()).hexdigest()
