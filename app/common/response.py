"""
Common API Response Envelope Module
Provides the standard enterprise response structure models and builder helper.
"""
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class StatusItem(BaseModel):
    statusCode: int = Field(..., description="HTTP status code")
    statusType: str = Field(..., description="'success' | 'error' | 'info'")
    statusDesc: str = Field(..., description="Human-readable description of the status")


class ResponseStatusList(BaseModel):
    statusList: list[StatusItem] = Field(default_factory=list)


class ResponseObject(BaseModel, Generic[T]):
    data: T


class ApiResponse(BaseModel, Generic[T]):
    responseStatusList: ResponseStatusList
    responseObject: ResponseObject[T]


def build_response(
    status_code: int,
    status_desc: str,
    data: Any = None,
    path: str = "",
    method: str = "GET",
    status_type: Optional[str] = None,
    error_type: Optional[str] = None,
    error_details: Any = None,
) -> dict[str, Any]:
    """
    Builds the standardized enterprise response envelope:
    {
        "responseStatusList": {
            "statusList": [
                {
                    "statusCode": 409,
                    "statusType": "error",
                    "statusDesc": "User not found"
                }
            ]
        },
        "responseObject": {
            "data": { ... }
        }
    }
    """
    if status_type is None:
        status_type = "success" if status_code < 400 else "error"

    if status_code >= 400:
        if not error_type:
            try:
                error_type = HTTPStatus(status_code).phrase
            except ValueError:
                error_type = "Error"
        payload_data: dict[str, Any] = {
            "errorType": error_type,
            "errorDetails": error_details,
            "path": path,
            "method": method,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        }
        if isinstance(data, dict):
            payload_data.update(data)
    else:
        payload_data = data

    return {
        "responseStatusList": {
            "statusList": [
                {
                    "statusCode": status_code,
                    "statusType": status_type,
                    "statusDesc": status_desc,
                }
            ]
        },
        "responseObject": {
            "data": payload_data,
        },
    }
