from typing import Any


def success_response(message: str = "Success", data: Any = None) -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(message: str, errors: Any = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "success": False,
        "message": message,
    }
    if errors is not None:
        payload["errors"] = errors
    return payload
