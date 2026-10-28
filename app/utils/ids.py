import uuid


def generate_uuid() -> str:
    """Generate a unique string ID using UUID4."""
    return str(uuid.uuid4())
