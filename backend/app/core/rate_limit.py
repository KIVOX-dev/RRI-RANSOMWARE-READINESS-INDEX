"""Shared slowapi Limiter instance. Lives in its own module (rather than
app/main.py) so route modules — notably auth.py, which needs it on
/auth/login and /auth/register — can import it without a circular import on
the FastAPI app itself."""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
