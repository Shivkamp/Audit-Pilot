from __future__ import annotations

import os
import re
from pathlib import Path

from fastapi import UploadFile, status

from app.core.constants import ALLOWED_DOCUMENT_EXTENSIONS
from app.core.exceptions import AppException

_FILENAME_SANITIZER_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def get_file_extension(filename: str) -> str:
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def sanitize_filename(filename: str) -> str:
    if not filename or not filename.strip():
        raise AppException(
            message="Filename is required.",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_FILENAME",
        )

    base_name = Path(filename.strip()).name.replace("\x00", "")
    sanitized = _FILENAME_SANITIZER_PATTERN.sub("_", base_name).strip(" .")

    if not sanitized:
        raise AppException(
            message="Filename is invalid.",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_FILENAME",
        )

    return sanitized


def validate_file_extension(filename: str) -> str:
    extension = get_file_extension(filename)

    if not extension:
        raise AppException(
            message="File extension is required.",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_FILE_EXTENSION",
        )

    if extension.lower() not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise AppException(
            message=(
                "Unsupported file extension. Allowed extensions are: "
                ", ".join(sorted(ALLOWED_DOCUMENT_EXTENSIONS))
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="UNSUPPORTED_FILE_EXTENSION",
        )

    return extension.lower()


def generate_safe_filename(original_filename: str) -> str:
    """Build a lowercase, filesystem-safe storage filename.

    Expects an already-sanitized and extension-validated filename (i.e. the
    output of ``sanitize_filename`` whose extension has passed
    ``validate_file_extension``).  Callers are responsible for validation
    before calling this function.
    """
    extension = get_file_extension(original_filename)
    stem = Path(original_filename).stem
    safe_stem = _FILENAME_SANITIZER_PATTERN.sub("_", stem).strip("._-").lower()

    if not safe_stem:
        safe_stem = "document"

    return f"{safe_stem}{extension}"


def reset_upload_file_pointer(upload_file: UploadFile) -> None:
    upload_file.file.seek(0, os.SEEK_SET)


def get_upload_file_size(upload_file: UploadFile) -> int:
    current_position = upload_file.file.tell()
    upload_file.file.seek(0, os.SEEK_END)
    size = upload_file.file.tell()
    upload_file.file.seek(current_position, os.SEEK_SET)
    return int(size)
