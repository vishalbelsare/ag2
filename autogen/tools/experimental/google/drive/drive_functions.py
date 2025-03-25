# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from .....import_utils import require_optional_import
from ..model import GoogleFileInfo

__all__ = [
    "list_files",
]


@require_optional_import(
    [
        "googleapiclient",
    ],
    "google-api",
)
def list_files(service: Any, page_size: int) -> list[GoogleFileInfo]:
    response = service.files().list(pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
    result = response.get("files", [])
    if not isinstance(result, list):
        raise ValueError(f"Expected a list of files, but got {result}")
    result = [GoogleFileInfo(**file_info) for file_info in result]
    return result
