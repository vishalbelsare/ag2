# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

import io
from pathlib import Path
from typing import Any

from .....import_utils import optional_import_block, require_optional_import
from ..model import GoogleFileInfo

with optional_import_block():
    from googleapiclient.http import MediaIoBaseDownload


__all__ = [
    "download_file",
    "list_files",
]


@require_optional_import(
    [
        "googleapiclient",
    ],
    "google-api",
)
def list_files(service: Any, page_size: int) -> list[GoogleFileInfo]:
    response = service.files().list(pageSize=page_size, fields="nextPageToken, files(id, name, mimeType)").execute()
    result = response.get("files", [])
    if not isinstance(result, list):
        raise ValueError(f"Expected a list of files, but got {result}")
    result = [GoogleFileInfo(**file_info) for file_info in result]
    return result


def _get_file_extension(mime_type: str) -> str:
    """Returns the correct file extension for a given MIME type."""
    mime_extensions = {
        "application/vnd.google-apps.document": "pdf",  # Google Docs → PDF
        "application/vnd.google-apps.spreadsheet": "xlsx",  # Google Sheets → Excel
        "application/vnd.google-apps.presentation": "pdf",  # Google Slides → PDF
        "video/quicktime": "mov",  # QuickTime Video
        "application/vnd.google.colaboratory": "ipynb",  # Jupyter Notebook
        "application/pdf": "pdf",
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "text/plain": "txt",
        "application/zip": "zip",
    }
    return mime_extensions.get(mime_type, "")


@require_optional_import(
    [
        "googleapiclient",
    ],
    "google-api",
)
def download_file(service: Any, file_id: str, file_name: str, mime_type: str, download_folder: Path) -> str:
    """Download or export file based on its MIME type."""
    file_extension = _get_file_extension(mime_type)
    if not file_name.endswith(file_extension):
        file_name = f"{file_name}.{file_extension}"

    if mime_type.startswith("application/vnd.google-apps."):
        # Handle Google Docs, Sheets, Slides
        export_mime_types = {
            "application/vnd.google-apps.document": "application/pdf",  # Google Docs → PDF
            "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # Google Sheets → Excel
            "application/vnd.google-apps.presentation": "application/pdf",  # Google Slides → PDF
        }

        if mime_type in export_mime_types:
            request = service.files().export(fileId=file_id, mimeType=export_mime_types[mime_type])
        else:
            return f"❌ Cannot export this file type: {mime_type}"
    else:
        # Handle regular files (videos, images, PDFs, etc.)
        request = service.files().get_media(fileId=file_id)

    # Save file
    with io.BytesIO() as buffer:
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        file_path = download_folder / file_name
        with open(file_path, "wb") as f:
            f.write(buffer.getvalue())

    return f"✅ Downloaded: {file_name}"
