from typing import Optional, Any
import httpx
from config import settings

HEADERS = {"X-Internal-API-Key": settings.INTERNAL_API_KEY}
TIMEOUT = 10.0


async def get(path: str, params: dict = None) -> Optional[Any]:
    try:
        async with httpx.AsyncClient(base_url=settings.BACKEND_URL, timeout=TIMEOUT) as client:
            r = await client.get(path, params=params, headers=HEADERS)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        detail = ""
        try:
            detail = e.response.json().get("detail", "")
        except Exception:
            pass
        raise APIError(detail or str(e))
    except Exception as e:
        raise APIError("Server bilan bog'lanishda xatolik. Keyinroq urinib ko'ring.")


async def post(path: str, json: dict = None, params: dict = None) -> Optional[Any]:
    try:
        async with httpx.AsyncClient(base_url=settings.BACKEND_URL, timeout=TIMEOUT) as client:
            r = await client.post(path, json=json, params=params, headers=HEADERS)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        detail = ""
        try:
            detail = e.response.json().get("detail", "")
        except Exception:
            pass
        raise APIError(detail or str(e))
    except Exception as e:
        raise APIError("Server bilan bog'lanishda xatolik. Keyinroq urinib ko'ring.")


class APIError(Exception):
    pass
