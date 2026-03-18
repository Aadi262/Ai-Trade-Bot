from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=[],
)

# Named limit strings — import these in route files
SCAN_RATE_LIMIT = f"{settings.RATE_LIMIT_SCAN_PER_MINUTE}/minute"
SIGNAL_RATE_LIMIT = f"{settings.RATE_LIMIT_SIGNAL_PER_MINUTE}/minute"
