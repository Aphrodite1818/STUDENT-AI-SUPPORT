from urllib.parse import urlsplit, urlunsplit

from fastapi import Request

from app.config.settings import settings


def resolve_frontend_app_url(request: Request | None = None) -> str:
    if request is not None:
        origin = request.headers.get("origin", "").strip()
        if origin and origin.lower() != "null":
            return origin.rstrip("/")

        referer = request.headers.get("referer", "").strip()
        if referer:
            parsed = urlsplit(referer)
            if parsed.scheme and parsed.netloc:
                return urlunsplit((parsed.scheme, parsed.netloc, "", "", "")).rstrip("/")

    return settings.FRONTEND_APP_URL.strip().rstrip("/")
